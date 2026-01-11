from typing import List

from app.domains.documents.schemas import ChunkBase


def format_chunks_to_context(chunks: List[ChunkBase]) -> str:
    if not chunks:
        return "Дополнительная информация в базе данных не найдена."

    context_parts = []

    for i, chunk in enumerate(chunks, 1):
        # Формируем заголовок для каждого фрагмента
        header = f"--- ФРАГМЕНТ {i} | ИСТОЧНИК: {chunk.source} | СТРАНИЦА: {chunk.page_num} ---"

        # Собираем блок: заголовок + контент
        chunk_text = f"{header}\n{chunk.content.strip()}"
        context_parts.append(chunk_text)

    # Соединяем все части через двойной перенос строки
    return "\n\n".join(context_parts)
