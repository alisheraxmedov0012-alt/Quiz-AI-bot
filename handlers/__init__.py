from .material_handler import router as material_handler_router
from .study_mode import router as study_mode_router
from .flashcards import router as flashcards_router
from .ai_features import router as ai_features_router
from .exam_mode import router as exam_mode_router
from .gamification import router as gamification_router
from .start import router as start_router
from .editor_handler import router as editor_handler_router
from .error_bank import router as error_bank_router
from .repetition import router as repetition_router
from .bookmarks import router as bookmarks_router
from .search import router as search_router
from .battle_node import router as battle_node_router
from .daily_challenge import router as daily_challenge_router
from .referral import router as referral_router
from .admin_panel import router as admin_panel_router

# main.py asmoqchi bo'lgan routerlar ro'yxati
all_routers = [
    material_handler_router,
    study_mode_router,
    flashcards_router,
    ai_features_router,
    exam_mode_router,
    gamification_router,
    start_router,
    editor_handler_router,
    error_bank_router,
    repetition_router,
    bookmarks_router,
    search_router,
    battle_node_router,
    daily_challenge_router,
    referral_router,
    admin_panel_router
]

