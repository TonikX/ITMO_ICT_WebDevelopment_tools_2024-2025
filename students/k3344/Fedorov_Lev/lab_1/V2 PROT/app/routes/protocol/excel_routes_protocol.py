from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from pathlib import Path
from ..protocol.excel_utils import fill_excel_template
from ...config import TEMPLATES_DIR, EXCEL_TEMPLATES_DIR, FILLED_PROTOCOLS_DIR

router = APIRouter(
    prefix="/protocol",
    tags=["protocol"],
    responses={401: {"description": "Unauthorized"}}
)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

protocol_data = {
    "match_number": "",
    "spectators": "",
    "team_a": {
        "name": "",
        "head_coach": "",
        "players": []
    },
    "team_b": {
        "name": "",
        "head_coach": "",
        "players": []
    },
    "periods": {
        "1": {"a": "", "b": ""},
        "2": {"a": "", "b": ""},
        "3": {"a": "", "b": ""},
        "ot": {"a": "", "b": ""},
        "so": {"a": "", "b": ""},
        "total": {"a": "", "b": ""}
    },
    "penalties": {
        "a": "",
        "b": ""
    },
    "shootout": [],
    "goalie_time": [],
    "officials": {
        "main_referee": "",
        "linesmen": "",
        "reserve_referee": "",
        "scorekeeper": "",
        "timekeeper": "",
        "penalty_box_officials": "",
        "goal_judges": "",
        "announcer": "",
        "inspector": "",
        "scorekeepers": ""
    },
    "timeouts": {
        "a": "",
        "b": ""
    }
}


@router.get("/protocol_table", response_class=HTMLResponse, operation_id="protocol_get_form")
async def get_form(request: Request):
    return templates.TemplateResponse("protocol_form.html", {"request": request, "protocol": protocol_data})

@router.post("/save", response_class=HTMLResponse, operation_id="protocol_save_data")
async def save_protocol(request: Request):
    form_data = await request.form()
    global protocol_data

    # team A players
    for i in range(20):
        player_number = form_data.get(f"team_a_player_{i}_number", "")
        if player_number:
            protocol_data["team_a"]["players"].append({
                "number": player_number,
                "name": form_data.get(f"team_a_player_{i}_name", ""),
                "captain": form_data.get(f"team_a_player_{i}_captain", ""),
                "position": form_data.get(f"team_a_player_{i}_position", ""),
                "participated": f"team_a_player_{i}_participated" in form_data
            })

    #team B players
    for i in range(20):
        player_number = form_data.get(f"team_b_player_{i}_number", "")
        if player_number:
            protocol_data["team_b"]["players"].append({
                "number": player_number,
                "name": form_data.get(f"team_b_player_{i}_name", ""),
                "captain": form_data.get(f"team_b_player_{i}_captain", ""),
                "position": form_data.get(f"team_b_player_{i}_position", ""),
                "participated": f"team_b_player_{i}_participated" in form_data
            })

    #goals for team A
    for i in range(20):
        goal_number = form_data.get(f"team_a_goal_{i}_number", "")
        if goal_number:
            protocol_data["goals_a"].append({
                "number": goal_number,
                "time": form_data.get(f"team_a_goal_{i}_time", ""),
                "scorer": form_data.get(f"team_a_goal_{i}_scorer", ""),
                "assist1": form_data.get(f"team_a_goal_{i}_assist1", ""),
                "assist2": form_data.get(f"team_a_goal_{i}_assist2", ""),
                "situation": form_data.get(f"team_a_goal_{i}_situation", "")
            })

    #goals for team B
    for i in range(20):
        goal_number = form_data.get(f"team_b_goal_{i}_number", "")
        if goal_number:
            protocol_data["goals_b"].append({
                "number": goal_number,
                "time": form_data.get(f"team_b_goal_{i}_time", ""),
                "scorer": form_data.get(f"team_b_goal_{i}_scorer", ""),
                "assist1": form_data.get(f"team_b_goal_{i}_assist1", ""),
                "assist2": form_data.get(f"team_b_goal_{i}_assist2", ""),
                "situation": form_data.get(f"team_b_goal_{i}_situation", "")
            })

    #penalties for team A
    for i in range(20):
        penalty_number = form_data.get(f"team_a_penalty_{i}_number", "")
        if penalty_number:
            protocol_data["penalties_a"].append({
                "number": penalty_number,
                "time": form_data.get(f"team_a_penalty_{i}_time", ""),
                "infraction": form_data.get(f"team_a_penalty_{i}_infraction", ""),
                "start": form_data.get(f"team_a_penalty_{i}_start", ""),
                "end": form_data.get(f"team_a_penalty_{i}_end", "")
            })

    # penalties for team B
    for i in range(20):
        penalty_number = form_data.get(f"team_b_penalty_{i}_number", "")
        if penalty_number:
            protocol_data["penalties_b"].append({
                "number": penalty_number,
                "time": form_data.get(f"team_b_penalty_{i}_time", ""),
                "infraction": form_data.get(f"team_b_penalty_{i}_infraction", ""),
                "start": form_data.get(f"team_b_penalty_{i}_start", ""),
                "end": form_data.get(f"team_b_penalty_{i}_end", "")
            })

    #shootout data
    for i in range(1, 6):
        player_a = form_data.get(f"shootout_a{i}", "")
        player_b = form_data.get(f"shootout_b{i}", "")
        if player_a or player_b:
            protocol_data["shootout"].append({
                "player_a": player_a,
                "player_b": player_b,
                "goalie_a": form_data.get(f"shootout_goalie_a{i}", ""),
                "goalie_b": form_data.get(f"shootout_goalie_b{i}", ""),
                "result": form_data.get(f"shootout_result{i}", "")
            })

    # goalie time data
    for i in range(1, 4):
        time = form_data.get(f"goalie_time{i}", "")
        if time:
            protocol_data["goalie_time"].append({
                "time": time,
                "goalie_a": form_data.get(f"goalie_a{i}", ""),
                "goalie_b": form_data.get(f"goalie_b{i}", "")
            })

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return {"success": True, "message": "Протокол сохранен"}

    return templates.TemplateResponse(
        "protocol_form.html",
        {
            "request": request,
            "protocol": protocol_data,
            "success_message": "Протокол сохранен успешно"
        }
    )

@router.get("/export-excel", operation_id="protocol_export_excel")
async def export_excel():
    try:
        from app.config import TEMPLATE_EXCEL_PATH
        if not TEMPLATE_EXCEL_PATH.exists():
            return {"error": f"Шаблон Excel не найден по пути: {TEMPLATE_EXCEL_PATH}"}
        filled_file_path = fill_excel_template(protocol_data)
        return FileResponse(
            path=filled_file_path,
            filename=Path(filled_file_path).name,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        print(f"Ошибка при экспорте Excel: {e}")
        return {"error": f"Не удалось создать Excel-файл: {str(e)}"}

@router.get("/templates", operation_id="protocol_list_templates")
async def list_templates():
    try:
        templates_list = []
        for file in EXCEL_TEMPLATES_DIR.glob("*.xlsx"):
            templates_list.append({
                "name": file.name,
                "path": str(file),
                "size": file.stat().st_size,
                "modified": datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            })
        return {"templates": templates_list}
    except Exception as e:
        return {"error": f"Ошибка при получении списка шаблонов: {str(e)}"}

@router.get("/filled", operation_id="protocol_list_filled")
async def list_filled_protocols():
    try:
        protocols = []
        for file in FILLED_PROTOCOLS_DIR.glob("*.xlsx"):
            protocols.append({
                "name": file.name,
                "path": str(file),
                "size": file.stat().st_size,
                "modified": datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            })
        return {"protocols": protocols}
    except Exception as e:
        return {"error": f"Ошибка при получении списка протоколов: {str(e)}"}
