from groq import Groq
from search import load_retriever, search, lookup, is_direct_name, is_lookup
from apikey import API_KEY


GROQ_API_KEY = API_KEY
GROQ_MODEL   = "meta-llama/llama-4-scout-17b-16e-instruct"

llm = Groq(api_key=GROQ_API_KEY)


SYSTEM_PROMPT = """Bạn là trợ lý tư vấn laptop chuyên nghiệp tại cửa hàng công nghệ. Nhiệm vụ của bạn là giúp khách hàng tìm được chiếc laptop phù hợp nhất dựa trên nhu cầu và sở thích của họ. Bạn sẽ dựa vào dữ liệu laptop có sẵn để đưa ra lời khuyên chính xác và hữu ích.

Nhiệm vụ:
- Dựa vào danh sách laptop được cung cấp, tư vấn cho khách hàng một cách tự nhiên, thân thiện.
- Giải thích tại sao laptop đó phù hợp với nhu cầu của khách.
- Nếu có nhiều lựa chọn, so sánh ngắn gọn và đưa ra gợi ý tốt nhất.
- Nếu không tìm thấy laptop phù hợp, xin lỗi và gợi ý khách mô tả lại nhu cầu.
- Trả lời bằng tiếng Việt, ngắn gọn, dễ hiểu, không quá 300 từ.
- Không bịa thêm thông tin ngoài dữ liệu được cung cấp.
- nếu là tư vấn laptop thông thường hãy chỉ ra cả 6 máy của top 6 sau truy vấn
- nếu khách hỏi về một máy cụ thể, hãy chỉ trả lời về máy đó, không cần nhắc đến các máy khác
- khi được yêu cầu so sánh, nếu người dùng yêu cầu so sánh một máy cụ thể thì làm theo yêu cầu, còn không hãy so sánh với những máy trong cùng phân khúc giá hoặc cấu hình
- khi cuộc trò chuyện diễn ra hãy tập chung trả lời câu hỏi, không cần giới thiệu bạn là ai nữa
"""


def format_search_context(results: list[dict]) -> str:
    if not results:
        return "Không tìm thấy laptop phù hợp."

    lines = []
    for r in results:
        lines.append(
            f"- {r['name']}\n"
            f"  CPU: {r['cpu']} | RAM: {r['ram']}GB | Storage: {r['storage']}GB\n"
            f"  GPU: {r['gpu']}\n"
            f"  Màn hình: {r['screen_size']} inch | Giá: {r['price']:,.0f}đ | Rating: {r['rating']}/5\n"
            f"  Mô tả: {r['mo_ta'][:200]}..."
        )
    return "\n".join(lines)


def format_lookup_context(result: dict) -> str:
    if not result:
        return "Không tìm thấy thông tin máy."

    return (
        f"- {result['name']}\n"
        f"  Hãng: {result['brand']} | CPU: {result['cpu']}\n"
        f"  RAM: {result['ram']}GB | Storage: {result['storage']}GB\n"
        f"  GPU: {result['gpu']}\n"
        f"  Màn hình: {result['screen_size']} inch | Giá: {result['price']:,.0f}đ | Rating: {result['rating']}/5\n"
        f"  Mô tả: {result['mo_ta']}"
    )


def ask_llm(user_query: str, context: str, history: list) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for h in history[-3:]:
        messages.append({"role": "user",      "content": h["user"]})
        messages.append({"role": "assistant", "content": h["assistant"]})

    messages.append({
        "role": "user",
        "content": (
            f"--- Dữ liệu laptop tìm được ---\n{context}\n\n"
            f"--- Câu hỏi của khách ---\n{user_query}"
        )
    })

    response = llm.chat.completions.create(
        model    = GROQ_MODEL,
        messages = messages,
    )
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    model, collection = load_retriever()
    history = []

    print("=" * 60)
    print("TƯ VẤN LAPTOP AI  |  'exit' để thoát")
    print("=" * 60)

    while True:
        query = input("Bạn: ").strip()
        if query.lower() == "exit":
            break
        if not query:
            continue

        if is_direct_name(query) or is_lookup(query):
            result  = lookup(query, model, collection)
            context = format_lookup_context(result)
        else:
            results, _ = search(query, model, collection, top_k=5)
            context    = format_search_context(results)

        answer = ask_llm(query, context, history)
        print(f"\n{answer}\n")

        history.append({"user": query, "assistant": answer})
