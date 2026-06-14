import asyncio
import os
import hmac
import hashlib
import urllib.parse
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Header, UploadFile, File, Form, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from loguru import logger
from telethon.sessions import StringSession

from core.config import BOT_TOKEN, GROQ_API_KEY, OPENROUTER_API_KEY
from database.database import (
    db, User, TelegramGroup, Groups, Account, UserAccountsTable,
    create_keywords_model, create_group_model, get_user_accounts, get_tracked_channels_count, get_target_group_count, get_session_count, get_keywords_count,
    getting_number_records_database, get_all_questions
)
from system.dispatcher import ADMIN_USER_ID
from locales.locales import t
from account_manager.auth import CheckingAccountsValidity, get_account_info
from account_manager.parser import (
    filter_messages, stop_tracking, active_clients, stop_flags
)
from ai.ai import get_groq_response, search_groups_in_telegram

# Initialize FastAPI
app = FastAPI(title="AutoParseAlertBot Web API", version="0.0.9")

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock Message for compatibility with Bot Handlers
class MockMessage:
    def __init__(self, user_id: int, username: Optional[str] = "web_user"):
        self.from_user = type('User', (), {
            'id': user_id,
            'username': username or 'web_user',
            'first_name': 'Web',
            'last_name': 'User'
        })()
        self.chat = type('Chat', (), {'id': user_id})()
        
        # Access bot lazily to prevent circular dependencies or uninitialized variables
        from system.dispatcher import bot
        self.bot = bot

    async def answer(self, text: str, reply_markup=None, parse_mode=None, **kwargs):
        from system.dispatcher import bot
        try:
            await bot.send_message(chat_id=self.from_user.id, text=text, parse_mode=parse_mode)
        except Exception as e:
            logger.error(f"Failed to send mock answer to {self.from_user.id}: {e}")

    async def answer_document(self, document, caption=None, parse_mode=None, **kwargs):
        from system.dispatcher import bot
        try:
            from aiogram.types import BufferedInputFile, FSInputFile
            if isinstance(document, BufferedInputFile):
                await bot.send_document(chat_id=self.from_user.id, document=document, caption=caption, parse_mode=parse_mode)
            elif isinstance(document, FSInputFile):
                await bot.send_document(chat_id=self.from_user.id, document=document, caption=caption, parse_mode=parse_mode)
        except Exception as e:
            logger.error(f"Failed to send mock document to {self.from_user.id}: {e}")

# Database Connection Middleware
@app.middleware("http")
async def db_session_middleware(request, call_next):
    if db.is_closed():
        db.connect(reuse_if_open=True)
    try:
        response = await call_next(request)
    finally:
        if not db.is_closed():
            db.close()
    return response

# Dependency to check auth from initData
def get_current_tg_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
        
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization scheme")
        
    token = authorization[7:]
    
    # Allow mock login for local development and testing
    if token.startswith("mock_"):
        try:
            mock_id = int(token.split("_")[1])
            is_admin = mock_id in ADMIN_USER_ID
            return {
                "id": mock_id,
                "first_name": "Test",
                "last_name": "User",
                "username": f"test_user_{mock_id}",
                "language_code": "ru",
                "is_mock": True
            }
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid mock token")
            
    try:
        params = dict(urllib.parse.parse_qsl(token))
        if 'hash' not in params:
            raise HTTPException(status_code=401, detail="Missing hash parameter")
            
        auth_hash = params.pop('hash')
        sorted_params = sorted(params.items())
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted_params)
        
        # Verify hash
        secret_key = hmac.new("WebAppData".encode(), BOT_TOKEN.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        if not hmac.compare_digest(calculated_hash, auth_hash):
            raise HTTPException(status_code=401, detail="Invalid Telegram signature")
            
        user_data = json.loads(params['user'])
        return user_data
    except Exception as e:
        logger.error(f"Telegram auth failed: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

# Global admin status dictionary for showing progress to admin in Web UI
admin_task_status = {
    "action": "none",     # "categorize", "lang_detect", "check_accounts", "actualize", "none"
    "progress": 0,
    "total": 0,
    "status": "idle",     # "running", "completed", "error"
    "message": ""
}

# Ensure directories exist
def init_web_directories():
    os.makedirs("web/static", exist_ok=True)
    os.makedirs("web/static/css", exist_ok=True)
    os.makedirs("web/static/js", exist_ok=True)

init_web_directories()

# ==================== PUBLIC API ENDPOINTS ====================

@app.get("/api/status")
async def get_status(user_data: dict = Depends(get_current_tg_user)):
    user_id = user_data["id"]
    
    # Get user
    user = User.get_or_none(User.user_id == user_id)
    if not user:
        # Register user in database
        user = User.create(
            user_id=user_id,
            username=user_data.get("username"),
            first_name=user_data.get("first_name"),
            last_name=user_data.get("last_name"),
            language="unset"
        )
    
    user_lang = user.language if user.language != "unset" else "ru"
    
    # Get stats
    groups_count = getting_number_records_database()
    session_count = get_session_count(user_id=user_id)
    group_count = get_target_group_count(user_id=user_id)
    tracked_channels = get_tracked_channels_count(user_id=user_id)
    keywords_count = get_keywords_count(user_id=user_id)
    
    # Get current target group username
    GroupModel = create_group_model(user_id)
    target_group = None
    if GroupModel.table_exists():
        groups = list(GroupModel.select())
        if groups:
            target_group = groups[0].user_group

    tracking_active = str(user_id) in active_clients
    is_admin = user_id in ADMIN_USER_ID

    return {
        "user_id": user_id,
        "username": user.username,
        "first_name": user.first_name,
        "language": user.language,
        "stars": user.stars,
        "is_admin": is_admin,
        "stats": {
            "version": "0.0.9",
            "db_total_groups": groups_count,
            "connected_accounts": session_count,
            "target_groups": group_count,
            "tracked_channels": tracked_channels,
            "keywords": keywords_count,
            "target_group_username": target_group
        },
        "tracking_active": tracking_active
    }

@app.post("/api/settings/language")
async def update_language(lang: str, user_data: dict = Depends(get_current_tg_user)):
    if lang not in ["ru", "en"]:
        raise HTTPException(status_code=400, detail="Invalid language code")
        
    user_id = user_data["id"]
    user = User.get_or_none(User.user_id == user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.language = lang
    user.save()
    return {"status": "ok", "language": lang}

@app.post("/api/tracking/start")
async def start_user_tracking(background_tasks: BackgroundTasks, user_data: dict = Depends(get_current_tg_user)):
    user_id = user_data["id"]
    user = User.get_or_none(User.user_id == user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if str(user_id) in active_clients:
        return {"status": "already_running"}

    # Start tracking asynchronously
    mock_msg = MockMessage(user_id=user_id, username=user.username)
    background_tasks.add_task(filter_messages, message=mock_msg, user_id=user_id, user=user)
    
    return {"status": "starting"}

@app.post("/api/tracking/stop")
async def stop_user_tracking(user_data: dict = Depends(get_current_tg_user)):
    user_id = user_data["id"]
    user = User.get_or_none(User.user_id == user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if str(user_id) not in stop_flags:
        return {"status": "not_active"}
        
    mock_msg = MockMessage(user_id=user_id, username=user.username)
    await stop_tracking(user_id=user_id, message=mock_msg)
    
    return {"status": "stopping"}

# Keywords Management
@app.get("/api/keywords")
async def list_keywords(user_data: dict = Depends(get_current_tg_user)):
    user_id = user_data["id"]
    KeywordsModel = create_keywords_model(user_id)
    
    if not KeywordsModel.table_exists():
        KeywordsModel.create_table()
        
    keywords = list(KeywordsModel.select())
    return [{"id": kw.id, "keyword": kw.user_keyword} for kw in keywords]

@app.post("/api/keywords")
async def add_keyword(keyword: str = Form(...), user_data: dict = Depends(get_current_tg_user)):
    user_id = user_data["id"]
    keyword = keyword.strip()
    if not keyword:
        raise HTTPException(status_code=400, detail="Keyword cannot be empty")
        
    KeywordsModel = create_keywords_model(user_id)
    if not KeywordsModel.table_exists():
        KeywordsModel.create_table()
        
    try:
        KeywordsModel.create(user_keyword=keyword)
        return {"status": "ok", "keyword": keyword}
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(status_code=400, detail="Keyword already exists")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/keywords/{kw_id}")
async def delete_keyword(kw_id: int, user_data: dict = Depends(get_current_tg_user)):
    user_id = user_data["id"]
    KeywordsModel = create_keywords_model(user_id)
    
    if not KeywordsModel.table_exists():
        raise HTTPException(status_code=404, detail="Keyword table not found")
        
    deleted = KeywordsModel.delete().where(KeywordsModel.id == kw_id).execute()
    if deleted:
        return {"status": "ok"}
    raise HTTPException(status_code=404, detail="Keyword not found")

# Tracked Channels Management
@app.get("/api/channels")
async def list_channels(user_data: dict = Depends(get_current_tg_user)):
    user_id = user_data["id"]
    records = list(Groups.select().where(Groups.user_id == user_id).order_by(Groups.date_added.desc()))
    return [{"id": ch.id, "username": ch.username, "date_added": ch.date_added.strftime("%Y-%m-%d %H:%M:%S")} for ch in records]

@app.post("/api/channels")
async def add_channel(username: str = Form(...), user_data: dict = Depends(get_current_tg_user)):
    user_id = user_data["id"]
    username = username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="Username cannot be empty")
        
    if not username.startswith("@"):
        username = f"@{username}"
        
    try:
        Groups.create(user_id=user_id, username=username)
        return {"status": "ok", "username": username}
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(status_code=400, detail="Channel already tracked")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/channels/{ch_id}")
async def delete_channel(ch_id: int, user_data: dict = Depends(get_current_tg_user)):
    user_id = user_data["id"]
    deleted = Groups.delete().where(Groups.user_id == user_id, Groups.id == ch_id).execute()
    if deleted:
        return {"status": "ok"}
    raise HTTPException(status_code=404, detail="Channel not found")

@app.post("/api/channels/upload")
async def upload_channels_file(file: UploadFile = File(...), user_data: dict = Depends(get_current_tg_user)):
    user_id = user_data["id"]
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are supported")
        
    contents = await file.read()
    text = contents.decode("utf-8")
    usernames = [line.strip() for line in text.splitlines() if line.strip()]
    
    added_count = 0
    skipped_count = 0
    errors_count = 0
    
    for username in usernames:
        if not username.startswith("@"):
            username = f"@{username}"
        try:
            Groups.create(user_id=user_id, username=username)
            added_count += 1
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                skipped_count += 1
            else:
                errors_count += 1
                
    return {
        "status": "ok",
        "added": added_count,
        "skipped": skipped_count,
        "errors": errors_count
    }

# Target Group Configuration
@app.get("/api/target-group")
async def get_target_group(user_data: dict = Depends(get_current_tg_user)):
    user_id = user_data["id"]
    GroupModel = create_group_model(user_id)
    if not GroupModel.table_exists():
        return {"username": None}
        
    groups = list(GroupModel.select())
    if groups:
        return {"username": groups[0].user_group}
    return {"username": None}

@app.post("/api/target-group")
async def set_target_group(username: str = Form(...), user_data: dict = Depends(get_current_tg_user)):
    user_id = user_data["id"]
    username = username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="Username cannot be empty")
        
    if not username.startswith("@"):
        username = f"@{username}"
        
    GroupModel = create_group_model(user_id)
    if not GroupModel.table_exists():
        GroupModel.create_table()
        
    # Clear previous group
    GroupModel.delete().execute()
    
    try:
        GroupModel.create(user_group=username)
        return {"status": "ok", "username": username}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Telegram Accounts Management
@app.get("/api/accounts")
async def list_accounts(user_data: dict = Depends(get_current_tg_user)):
    user_id = user_data["id"]
    accounts = get_user_accounts(user_id)
    # Return serializable dict (excluding the full session string)
    return [
        {
            "phone_number": acc["phone_number"],
            "created_at": acc["created_at"].strftime("%Y-%m-%d %H:%M:%S")
        }
        for acc in accounts
    ]

@app.post("/api/accounts/upload")
async def upload_account_session(file: UploadFile = File(...), user_data: dict = Depends(get_current_tg_user)):
    user_id = user_data["id"]
    user = User.get_or_none(User.user_id == user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if not file.filename.endswith(".session"):
        raise HTTPException(status_code=400, detail="Only .session files are supported")
        
    # Make temporary accounts directory
    sessions_dir = Path("accounts")
    sessions_dir.mkdir(exist_ok=True)
    
    # Sanitize and write session file
    safe_name = "".join(c for c in file.filename if c.isalnum() or c in "._-")
    temp_path = sessions_dir / f"temp_{user_id}_{safe_name}"
    
    try:
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
            
        session_path_without_ext = str(temp_path.with_suffix(""))
        mock_msg = MockMessage(user_id=user_id, username=user.username)
        checker = CheckingAccountsValidity(message=mock_msg, path=session_path_without_ext)
        client = await checker.connect_client()
        
        if client:
            account_info = await get_account_info(client)
            phone = account_info["phone"] or "unknown"
            session_string = StringSession.save(client.session)
            
            # Save account to user table
            from database.database import write_account_to_user_table
            write_account_to_user_table(
                user_id=user_id,
                session_string=session_string,
                phone_number=phone
            )
            
            await client.disconnect()
            
            # Send notification via Bot
            user_lang = user.language if user.language != "unset" else "ru"
            await mock_msg.answer(t("session_connected_success", lang=user_lang, filename=safe_name, phone=phone, name=account_info["first_name"]))
            
            return {"status": "ok", "phone": phone, "name": account_info["first_name"]}
        else:
            raise HTTPException(status_code=400, detail="Session file is invalid or not authorized")
    except Exception as e:
        logger.exception(f"Error processing session file upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_path.exists():
            temp_path.unlink()

@app.delete("/api/accounts/{phone}")
async def delete_account(phone: str, user_data: dict = Depends(get_current_tg_user)):
    user_id = user_data["id"]
    
    # Retrieve user account list to find the session string matching this phone
    accounts = get_user_accounts(user_id)
    session_to_delete = None
    for acc in accounts:
        if acc["phone_number"] == phone:
            session_to_delete = acc["session_string"]
            break
            
    if not session_to_delete:
        raise HTTPException(status_code=404, detail="Account not found")
        
    # Delete from user accounts table
    deleted = UserAccountsTable.delete().where(
        UserAccountsTable.user_id == user_id,
        UserAccountsTable.phone_number == phone
    ).execute()
    
    if deleted:
        # Also clean from global active clients if connected
        if str(user_id) in active_clients:
            # We must disconnect active client
            client = active_clients.pop(str(user_id))
            if client.is_connected():
                await client.disconnect()
            if str(user_id) in stop_flags:
                stop_flags.pop(str(user_id))
        return {"status": "ok"}
        
    raise HTTPException(status_code=500, detail="Failed to delete account")

# Stars Top Up Invoice Link
@app.post("/api/payment/stars-topup")
async def create_topup_invoice(amount: int = Query(...), user_data: dict = Depends(get_current_tg_user)):
    user_id = user_data["id"]
    user = User.get_or_none(User.user_id == user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_lang = user.language if user.language != "unset" else "ru"
    
    from system.dispatcher import bot
    from aiogram.types import LabeledPrice
    
    try:
        invoice_link = await bot.create_invoice_link(
            title=t("stars_invoice_title", lang=user_lang),
            description=t("stars_invoice_desc", lang=user_lang, amount=amount),
            payload=f"topup_stars_{amount}",
            provider_token="",  # must be empty for Telegram Stars
            currency="XTR",
            prices=[LabeledPrice(label="Stars", amount=amount)]
        )
        return {"invoice_link": invoice_link}
    except Exception as e:
        logger.exception(f"Error creating invoice link: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# AI Group Search Endpoint
@app.post("/api/search/ai")
async def trigger_ai_search(query: str = Form(...), user_data: dict = Depends(get_current_tg_user)):
    user_id = user_data["id"]
    user = User.get_or_none(User.user_id == user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_lang = user.language if user.language != "unset" else "ru"
    
    # Try generating names
    try:
        answer = await get_groq_response(query)
        from handlers.user.pars_ai import clean_group_name, save_group_to_db
        group_names = [clean_group_name(line) for line in answer.splitlines() if line.strip()]
        group_names = [name for name in group_names if len(name) > 2]
        
        if not group_names:
            return {"status": "no_names_generated", "groups": []}
            
        mock_msg = MockMessage(user_id=user_id, username=user.username)
        checker = CheckingAccountsValidity(message=mock_msg)
        client = await checker.start_random_client()
        
        if not client:
            raise HTTPException(status_code=400, detail="No active Telegram accounts available for search")
            
        saved_groups = []
        for name in group_names:
            results = await search_groups_in_telegram(client=client, group_names=[name])
            for group_data in results:
                saved = save_group_to_db(group_data)
                if saved:
                    saved_groups.append({
                        "name": saved.name,
                        "username": saved.username,
                        "participants": saved.participants,
                        "group_type": saved.group_type,
                        "availability": saved.availability,
                        "link": saved.link
                    })
                    
        await client.disconnect()
        return {"status": "ok", "groups": saved_groups}
    except Exception as e:
        logger.exception(f"AI search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get Database / Export XLSX Endpoint
@app.get("/api/export/check")
async def check_export_status(user_data: dict = Depends(get_current_tg_user)):
    user_id = user_data["id"]
    user = User.get_or_none(User.user_id == user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    from handlers.user.pars_ai import can_user_download_free
    is_free, remaining = can_user_download_free(user)
    return {
        "is_free": is_free,
        "remaining_seconds": remaining,
        "stars_balance": user.stars
    }

@app.post("/api/export/download")
async def download_database(
    export_type: str = Form("all"), # "all", "channels", "groups"
    category: Optional[str] = Form(None), # e.g. "investments"
    user_data: dict = Depends(get_current_tg_user)
):
    user_id = user_data["id"]
    user = User.get_or_none(User.user_id == user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Check if download is free or requires Stars
    from handlers.user.pars_ai import can_user_download_free
    is_free, remaining = can_user_download_free(user)
    
    if not is_free:
        # Needs to deduct 5 Stars from balance
        if user.stars < 5:
            raise HTTPException(
                status_code=402, 
                detail="Payment required: Need 5 Telegram Stars to download before 24h limit expires"
            )
        # Deduct
        user.stars -= 5
        user.save()
        logger.info(f"Deducted 5 Stars from {user_id}. New balance: {user.stars}")
    else:
        # Record free download timestamp
        user.last_free_download_at = datetime.now()
        user.save()
        
    # Query groups
    query = TelegramGroup.select()
    if export_type == "channels":
        query = query.where(TelegramGroup.group_type == "Канал")
    elif export_type == "groups":
        query = query.where(TelegramGroup.group_type != "Канал")
        
    if category and category != "all":
        query = query.where(TelegramGroup.category == category.lower())
        
    groups = list(query)
    
    # Generate Excel in memory
    from handlers.user.pars_ai import create_excel_file
    user_lang = user.language if user.language != "unset" else "ru"
    excel_bytes = create_excel_file(groups, lang=user_lang)
    
    filename = f"db_export_{export_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    # Return as streaming response
    return StreamingResponse(
        io_bytes_stream(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

def io_bytes_stream(data: bytes):
    import io
    stream = io.BytesIO(data)
    yield from stream

# ==================== ADMIN PANEL API ENDPOINTS ====================

def require_admin(user_data: dict = Depends(get_current_tg_user)):
    user_id = user_data["id"]
    if user_id not in ADMIN_USER_ID:
        raise HTTPException(status_code=403, detail="Access denied: Admin only")
    return user_id

@app.get("/api/admin/status")
async def get_admin_status(user_id: int = Depends(require_admin)):
    # Calculate groups without category
    uncategorized_count = TelegramGroup.select().where(
        (TelegramGroup.username.is_null(False)) &
        (TelegramGroup.category == '')
    ).count()
    
    # Get total accounts
    total_accounts = Account.select().count()
    
    return {
        "uncategorized_count": uncategorized_count,
        "total_accounts": total_accounts,
        "task": admin_task_status
    }

# Background Admin Tasks

async def bg_check_accounts():
    global admin_task_status
    admin_task_status["action"] = "check_accounts"
    admin_task_status["status"] = "running"
    admin_task_status["progress"] = 0
    admin_task_status["message"] = "Starting account verification..."
    
    try:
        available_sessions = getting_account()
        total = len(available_sessions)
        admin_task_status["total"] = total
        
        # We need a dummy MockMessage for CheckingAccountsValidity
        # Use first admin ID
        admin_id = list(ADMIN_USER_ID)[0]
        mock_msg = MockMessage(user_id=admin_id)
        checker = CheckingAccountsValidity(message=mock_msg)
        
        for idx, session in enumerate(available_sessions, 1):
            admin_task_status["progress"] = idx
            admin_task_status["message"] = f"Checking session {idx}/{total}..."
            await checker.verify_account(session)
            
        admin_task_status["status"] = "completed"
        admin_task_status["message"] = "Account check completed successfully!"
    except Exception as e:
        logger.exception(f"Error in bg_check_accounts: {e}")
        admin_task_status["status"] = "error"
        admin_task_status["message"] = f"Error: {e}"

async def bg_actualize_db():
    global admin_task_status
    admin_task_status["action"] = "actualize"
    admin_task_status["status"] = "running"
    admin_task_status["progress"] = 0
    admin_task_status["message"] = "Initializing database actualization..."
    
    try:
        available_sessions = getting_account()
        if not available_sessions:
            raise Exception("No active Telegram sessions available")
            
        groups_to_update = list(TelegramGroup.select().where(
            (TelegramGroup.username.is_null(False)) &
            (TelegramGroup.group_type == '')
        ))
        
        total = len(groups_to_update)
        admin_task_status["total"] = total
        
        if total == 0:
            admin_task_status["status"] = "completed"
            admin_task_status["message"] = "All database records are already actualized!"
            return

        # Setup checker
        admin_id = list(ADMIN_USER_ID)[0]
        mock_msg = MockMessage(user_id=admin_id)
        checker = CheckingAccountsValidity(message=mock_msg)
        
        client = await checker.client_connect_string_session(available_sessions[0])
        if not client:
            raise Exception("Failed to connect to Telegram client session")
            
        from telethon.tl.functions.channels import GetFullChannelRequest
        
        for idx, group in enumerate(groups_to_update, 1):
            admin_task_status["progress"] = idx
            admin_task_status["message"] = f"Updating {group.name or group.username} ({idx}/{total})..."
            
            try:
                entity = await client.get_entity(group.username)
                telegram_id = entity.id
                group_type = "Канал" if getattr(entity, 'broadcast', False) else "Группа"
                
                # Fetch full info
                full_channel = await client(GetFullChannelRequest(channel=entity))
                description = full_channel.full_chat.about or ""
                participants = full_channel.full_chat.participants_count or 0
                
                # Update DB
                TelegramGroup.update(
                    telegram_id=telegram_id,
                    group_type=group_type,
                    description=description,
                    participants=participants
                ).where(TelegramGroup.id == group.id).execute()
                
            except Exception as e:
                logger.warning(f"Failed to update group {group.username}: {e}")
                
            await asyncio.sleep(1.5)
            
        await client.disconnect()
        admin_task_status["status"] = "completed"
        admin_task_status["message"] = f"Database actualization finished! Updated {total} groups."
    except Exception as e:
        logger.exception(f"Error in bg_actualize_db: {e}")
        admin_task_status["status"] = "error"
        admin_task_status["message"] = f"Error: {e}"

async def bg_categorize_db(method: str):
    global admin_task_status
    admin_task_status["action"] = "categorize"
    admin_task_status["status"] = "running"
    admin_task_status["progress"] = 0
    admin_task_status["message"] = "Initializing category assignment..."
    
    try:
        from database.database import get_groups_without_category
        from ai.ai import category_assignment
        from handlers.admin.checking_group_for_ai import get_best_g4f_model
        
        # 1. Setup client based on method
        if method == "fast":
            from g4f.client import Client
            client = Client()
            model = await get_best_g4f_model(client)
        elif method == "openrouter":
            from openai import AsyncOpenAI
            client = AsyncOpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)
            model = "deepseek/deepseek-v4-flash"
        elif method == "groq":
            from groq import AsyncGroq
            client = AsyncGroq(api_key=GROQ_API_KEY)
            model = "llama-3.1-8b-instant"
        else:
            raise Exception(f"Unknown categorization method: {method}")
            
        groups_to_process = await get_groups_without_category()
        total = len(groups_to_process)
        admin_task_status["total"] = total
        
        if total == 0:
            admin_task_status["status"] = "completed"
            admin_task_status["message"] = "All groups already have categories!"
            return
            
        for idx, group_data in enumerate(groups_to_process, 1):
            admin_task_status["progress"] = idx
            admin_task_status["message"] = f"Categorizing {group_data['name']} ({idx}/{total})..."
            
            try:
                result = await category_assignment(group_data, client, model)
                if result.get("success") and result.get("category"):
                    category_lower = result["category"].lower()
                    TelegramGroup.update(category=category_lower).where(
                        TelegramGroup.telegram_id == result["telegram_id"]
                    ).execute()
            except Exception as e:
                logger.error(f"Failed to categorize {group_data['name']}: {e}")
                
            if method == "fast":
                await asyncio.sleep(0.5)
            else:
                await asyncio.sleep(0.2)
                
        admin_task_status["status"] = "completed"
        admin_task_status["message"] = f"Category assignment finished! Categorized {total} groups."
    except Exception as e:
        logger.exception(f"Error in bg_categorize_db: {e}")
        admin_task_status["status"] = "error"
        admin_task_status["message"] = f"Error: {e}"

async def bg_detect_language():
    global admin_task_status
    admin_task_status["action"] = "lang_detect"
    admin_task_status["status"] = "running"
    admin_task_status["progress"] = 0
    admin_task_status["message"] = "Initializing language detection..."
    
    try:
        from handlers.admin.language_detection import ai_llama_fri
        
        groups_to_detect = list(TelegramGroup.select().where(
            (TelegramGroup.username.is_null(False)) &
            ((TelegramGroup.language == '') | (TelegramGroup.language.is_null()))
        ))
        
        total = len(groups_to_detect)
        admin_task_status["total"] = total
        
        if total == 0:
            admin_task_status["status"] = "completed"
            admin_task_status["message"] = "All groups already have language set!"
            return
            
        for idx, group in enumerate(groups_to_detect, 1):
            admin_task_status["progress"] = idx
            admin_task_status["message"] = f"Detecting language for {group.name or group.username} ({idx}/{total})..."
            
            group_data = {
                "group_hash": group.group_hash,
                "name": group.name,
                "username": group.username,
                "description": group.description or ""
            }
            
            try:
                res = await asyncio.to_thread(ai_llama_fri, group_data, lang="ru")
                if res.get("success") and res.get("language"):
                    TelegramGroup.update(language=res["language"]).where(
                        TelegramGroup.group_hash == res["group_hash"]
                    ).execute()
            except Exception as e:
                logger.error(f"Failed to detect language for {group.name}: {e}")
                
            await asyncio.sleep(2.0)
            
        admin_task_status["status"] = "completed"
        admin_task_status["message"] = f"Language detection finished! Processed {total} groups."
    except Exception as e:
        logger.exception(f"Error in bg_detect_language: {e}")
        admin_task_status["status"] = "error"
        admin_task_status["message"] = f"Error: {e}"

@app.post("/api/admin/check-accounts")
async def admin_check_accounts(background_tasks: BackgroundTasks, user_id: int = Depends(require_admin)):
    if admin_task_status["status"] == "running":
        return {"status": "busy", "task": admin_task_status}
    background_tasks.add_task(bg_check_accounts)
    return {"status": "started"}

@app.post("/api/admin/actualize")
async def admin_actualize_db(background_tasks: BackgroundTasks, user_id: int = Depends(require_admin)):
    if admin_task_status["status"] == "running":
        return {"status": "busy", "task": admin_task_status}
    background_tasks.add_task(bg_actualize_db)
    return {"status": "started"}

@app.post("/api/admin/categorize")
async def admin_categorize_db(method: str = Query("fast"), background_tasks: BackgroundTasks = None, user_id: int = Depends(require_admin)):
    if admin_task_status["status"] == "running":
        return {"status": "busy", "task": admin_task_status}
    background_tasks.add_task(bg_categorize_db, method=method)
    return {"status": "started"}

@app.post("/api/admin/detect-language")
async def admin_detect_language(background_tasks: BackgroundTasks, user_id: int = Depends(require_admin)):
    if admin_task_status["status"] == "running":
        return {"status": "busy", "task": admin_task_status}
    background_tasks.add_task(bg_detect_language)
    return {"status": "started"}

@app.get("/api/admin/export-questions")
async def admin_export_questions(user_id: int = Depends(require_admin)):
    questions = get_all_questions()
    if not questions:
        raise HTTPException(status_code=404, detail="No questions found in database")
        
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["user_id", "question", "answer"])
    writer.writeheader()
    for q in questions:
        writer.writerow(q)
        
    filename = f"questions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return StreamingResponse(
        io_bytes_stream(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/api/admin/logs")
async def admin_download_logs(user_id: int = Depends(require_admin)):
    log_path = "logs/log.log"
    if not os.path.exists(log_path):
        raise HTTPException(status_code=404, detail="Log file not found")
    return FileResponse(log_path, media_type="text/plain", filename="bot_log.txt")

# Mount Static Files
app.mount("/", StaticFiles(directory="web/static", html=True), name="static")
