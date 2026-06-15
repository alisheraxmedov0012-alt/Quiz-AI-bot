from typing import Any, Callable, Dict, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
import time

class AntiSpamMiddleware(BaseMiddleware):
    def __init__(self, limit: int = 1) -> None:
        self.limit = limit
        self.storage = {} # {user_id: last_message_time}

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        current_time = time.time()
        
        if user_id in self.storage:
            last_time = self.storage[user_id]
            if current_time - last_time < self.limit:
                return await event.answer("⚠️ **Iltimos, ketma-ket tez xabar yubormang! (Anti-Spam)**")
                
        self.storage[user_id] = current_time
        return await handler(event, data)
      
