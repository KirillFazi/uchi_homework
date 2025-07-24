"""Промпты для RAG системы."""

# Системный промпт для RAG
SYSTEM_PROMPT = """You are a Moodle assistant. Use ONLY information from the provided context.

RULES:
1. Answer in Russian language
2. Give specific step-by-step instructions
3. Use information from the context above
4. Do not give general phrases
5. If the context contains specific instructions, include them in your answer

IMPORTANT: Extract and translate the specific steps from the context into Russian."""

# Промпт для построения контекста
CONTEXT_PROMPT = "CONTEXT:\n{context}"

# Промпт для истории диалога
HISTORY_PROMPT = "DIALOGUE HISTORY:\n{history}"

# Промпт для вопроса
QUESTION_PROMPT = "QUESTION: {question}"

# Промпт для ответа
ANSWER_PROMPT = "ANSWER:"


def build_prompt(question: str, context: str = "", history: str = "") -> str:
    """Строит полный промпт для LLM.
    
    Args:
        question: Вопрос пользователя
        context: Контекст из найденных документов
        history: История диалога
        
    Returns:
        Полный промпт для LLM
    """
    prompt_parts = [SYSTEM_PROMPT]
    
    if context:
        prompt_parts.append(CONTEXT_PROMPT.format(context=context))
    
    if history:
        prompt_parts.append(HISTORY_PROMPT.format(history=history))
    
    prompt_parts.append(QUESTION_PROMPT.format(question=question))
    prompt_parts.append(ANSWER_PROMPT)
    
    return "\n\n".join(prompt_parts) 