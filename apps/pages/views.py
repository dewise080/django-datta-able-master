import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.http import JsonResponse

from apps.pages.models import Product, UserTelegramCredential, UserWhatsAppInstance
from accounts_plus.models import UserN8NProfile
from n8n_mirror.models import UserApiKeys

EVOLUTION_API_URL = "https://evo.lotfinity.tech"
EVOLUTION_API_KEY = "123456789Tt@"

@login_required
def index(request):
  context = {
    'segment': 'dashboard'
  }
  return render(request, "pages/index.html", context)

# Components
def color(request):
  context = {
    'segment': 'color'
  }
  return render(request, "pages/color.html", context)

def typography(request):
  context = {
    'segment': 'typography'
  }
  return render(request, "pages/typography.html", context)

def icon_feather(request):
  context = {
    'segment': 'feather_icon'
  }
  return render(request, "pages/icon-feather.html", context)

@login_required
def credentials(request):
  print(f"[credentials] User authenticated: {request.user.is_authenticated}, User: {request.user}", flush=True)
  profile = UserN8NProfile.objects.filter(user=request.user).first()
  
  # Get API key if profile exists
  api_key_obj = None
  if profile and profile.n8n_user_id:
    api_key_obj = (
      UserApiKeys.objects.using("n8n")
      .filter(userId_id=str(profile.n8n_user_id))
      .exclude(label__iexact="MCP Server API Key")
      .order_by("-createdAt")
      .first()
    )

  existing_telegram = UserTelegramCredential.objects.filter(user=request.user)
  existing_whatsapp = UserWhatsAppInstance.objects.filter(user=request.user)

  if request.method == "POST":
    form_type = request.POST.get("form_type")
    
    # Handle Telegram form submission
    if form_type == "telegram":
      name = (request.POST.get("name") or "").strip()
      token = (request.POST.get("token") or "").strip()

      if not name or not token:
        messages.error(request, "Name and token are required.")
        return redirect("apps.pages:credentials")

      if not api_key_obj:
        messages.error(request, "No n8n API key found for your account.")
        return redirect("apps.pages:credentials")

      payload = {
        "name": name,
        "type": "telegramApi",
        "data": {"accessToken": token},
      }
      headers = {"X-N8N-API-KEY": api_key_obj.apiKey}

      try:
        print(
          f"[credentials] POST https://n8n.lotfinity.tech/api/v1/credentials "
          f"headers={{'X-N8N-API-KEY': '{api_key_obj.apiKey}'}} payload={payload}",
          flush=True,
        )
        resp = requests.post(
          "https://n8n.lotfinity.tech/api/v1/credentials",
          headers=headers,
          json=payload,
          timeout=10,
        )
        resp.raise_for_status()
        body = resp.json()
        n8n_cred_id = body.get("id") or body.get("data", {}).get("id")
        if not n8n_cred_id:
          raise ValueError("Credential ID missing from n8n response")

        UserTelegramCredential.objects.create(
          user=request.user,
          n8n_credential_id=n8n_cred_id,
          name=body.get("name") or name,
          token=token,
        )
        messages.success(request, "Telegram token saved and synced to n8n.")
        return redirect("apps.pages:credentials")
      except Exception as exc:
        print(
          f"[credentials][ERROR] status={getattr(resp, 'status_code', None)} "
          f"body={getattr(resp, 'text', None)}",
          flush=True,
        )
        messages.error(request, f"Failed to save credential: {exc}")
        return redirect("apps.pages:credentials")

    # Handle WhatsApp form submission
    elif form_type == "whatsapp":
      instance_name = (request.POST.get("instance_name") or "").strip()
      whatsapp_number = (request.POST.get("whatsapp_number") or "").strip()

      if not instance_name or not whatsapp_number:
        messages.error(request, "Instance name and WhatsApp number are required.")
        return redirect("apps.pages:credentials")

      # Check if instance name already exists
      if UserWhatsAppInstance.objects.filter(instance_name=instance_name).exists():
        messages.error(request, "An instance with this name already exists.")
        return redirect("apps.pages:credentials")

      payload = {
        "instanceName": instance_name,
        "integration": "WHATSAPP-BAILEYS",
        "number": whatsapp_number,
        "qrcode": True,
      }
      headers = {
        "apikey": EVOLUTION_API_KEY,
        "Content-Type": "application/json",
      }

      try:
        print(
          f"[whatsapp] POST {EVOLUTION_API_URL}/instance/create "
          f"payload={payload}",
          flush=True,
        )
        resp = requests.post(
          f"{EVOLUTION_API_URL}/instance/create",
          headers=headers,
          json=payload,
          timeout=15,
        )
        resp.raise_for_status()
        body = resp.json()
        print(f"[whatsapp] Response: {body}", flush=True)

        # Extract data from response
        instance_data = body.get("instance", {})
        qrcode_data = body.get("qrcode", {})
        
        # Save instance to database
        whatsapp_instance = UserWhatsAppInstance.objects.create(
          user=request.user,
          instance_name=instance_data.get("instanceName", instance_name),
          instance_id=instance_data.get("instanceId"),
          whatsapp_number=whatsapp_number,
          hash_key=body.get("hash"),
          status=instance_data.get("status", "connecting"),
        )
        
        # Store QR data in session for display
        request.session["whatsapp_qr_data"] = {
          "instance_name": whatsapp_instance.instance_name,
          "pairing_code": qrcode_data.get("pairingCode"),
          "qr_base64": qrcode_data.get("base64"),
          "code": qrcode_data.get("code"),
        }
        
        messages.success(request, "WhatsApp instance created! Scan the QR code to connect.")
        return redirect("apps.pages:whatsapp_connect", instance_name=whatsapp_instance.instance_name)
      except requests.exceptions.RequestException as exc:
        print(
          f"[whatsapp][ERROR] status={getattr(resp, 'status_code', None)} "
          f"body={getattr(resp, 'text', None)}",
          flush=True,
        )
        messages.error(request, f"Failed to create WhatsApp instance: {exc}")
        return redirect("apps.pages:credentials")

  context = {
    'segment': 'credentials',
    "credentials": existing_telegram,
    "whatsapp_instances": existing_whatsapp,
    "has_api_key": bool(api_key_obj),
    "has_profile": bool(profile),
  }
  return render(request, 'pages/credentials.html', context)


@login_required
def whatsapp_connect(request, instance_name):
    """Display QR code for WhatsApp instance connection."""
    instance = UserWhatsAppInstance.objects.filter(
        user=request.user, instance_name=instance_name
    ).first()

    if not instance:
        messages.error(request, "WhatsApp instance not found.")
        return redirect("apps.pages:credentials")

    # Get QR data from session (set during instance creation)
    qr_data = request.session.pop("whatsapp_qr_data", None)
    
    context = {
        "segment": "credentials",
        "instance": instance,
        "qr_data": qr_data,
    }
    return render(request, "pages/whatsapp_connect.html", context)


@login_required
def whatsapp_refresh_qr(request, instance_name):
    """API endpoint to refresh QR code for an existing instance."""
    instance = UserWhatsAppInstance.objects.filter(
        user=request.user, instance_name=instance_name
    ).first()

    if not instance:
        return JsonResponse({"error": "Instance not found"}, status=404)

    headers = {
        "apikey": EVOLUTION_API_KEY,
        "Content-Type": "application/json",
    }

    try:
        print(
            f"[whatsapp_qr] GET {EVOLUTION_API_URL}/instance/connect/{instance_name}",
            flush=True,
        )
        resp = requests.get(
            f"{EVOLUTION_API_URL}/instance/connect/{instance_name}",
            headers=headers,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        print(f"[whatsapp_qr] Response: {data}", flush=True)

        return JsonResponse({
            "pairingCode": data.get("pairingCode"),
            "base64": data.get("base64"),
            "code": data.get("code"),
            "count": data.get("count"),
        })
    except requests.exceptions.RequestException as exc:
        print(
            f"[whatsapp_qr][ERROR] status={getattr(resp, 'status_code', None)} "
            f"body={getattr(resp, 'text', None)}",
            flush=True,
        )
        return JsonResponse({"error": str(exc)}, status=500)
