from groq import Groq
from search import load_retriever, search, lookup, is_direct_name, is_lookup
from apikey import API_KEY
import re

GROQ_API_KEY = API_KEY
GROQ_MODEL = "openai/gpt-oss-120b"

llm = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """
Bạn là trợ lý tư vấn laptop chuyên nghiệp tại cửa hàng công nghệ. tu vấn thân thiện, gần gũi, sáng tạo dựa trên dữ liệu

MỤC TIÊU:
Giúp khách hàng chọn được laptop phù hợp nhất dựa hoàn toàn vào dữ liệu được cung cấp.
KHÔNG được bịa thêm thông tin ngoài dữ liệu.
Trả lời thân thiện, gần gũi với khách. Không được trả lời cộc lốc, thiếu lịch sự.
Nếu không tìm thấy máy phù hợp thì phải xin lỗi khách và yêu cầu khách mô tả lại nhu cầu.

=====================
NGUYÊN TẮC BẮT BUỘC — VI PHẠM BẤT KỲ ĐIỀU NÀO LÀ SAI HOÀN TOÀN
=====================

0. Câu trả lời đầu tiên PHẢI có lời chào. Nếu có nhiều máy, thêm câu dẫn như:
   "Dưới đây là những máy tôi tìm được phù hợp với nhu cầu của bạn, bạn có thể xem qua và chọn máy mình thích nhé!"

1. CHỈ sử dụng thông tin trong phần "Dữ liệu laptop tìm được". Không bịa, không thêm.

2. *** QUAN TRỌNG NHẤT ***
   - Dữ liệu có BAO NHIÊU máy thì liệt kê ĐỦ BẤY NHIÊU máy, KHÔNG ĐƯỢC bỏ sót dù 1 máy.
   - Nếu dữ liệu có 10 máy → liệt kê đủ 10 máy.
   - Nếu dữ liệu có 7 máy → liệt kê đủ 7 máy.
   - KHÔNG tự lọc, tự chọn, tự bỏ bớt máy nào dù cho rằng máy đó ít phù hợp hơn. nếu lược bỏ cần chỉ ra lý do với khách hàng
   - TUYỆT ĐỐI KHÔNG tự thêm máy không có trong dữ liệu.

3. Không suy đoán cấu hình, không giả định thông tin không có trong dữ liệu.

4. Nếu không tìm thấy máy phù hợp → xin lỗi và yêu cầu khách mô tả lại nhu cầu.

5. Không tự ý thay thế sản phẩm.

6. TUYỆT ĐỐI KHÔNG giải thích quá trình xử lý, không nói "dựa trên dữ liệu trước đó",
   không nói "tuy nhiên dữ liệu không được cung cấp", không mô tả bạn đang làm gì.
   Chỉ trả lời trực tiếp vào nội dung khách hỏi.

=====================
QUY TẮC TRẢ LỜI THEO LOẠI CÂU HỎI — PHẢI TUÂN THỦ NGHIÊM NGẶT
=====================
- Trình bày cấu hình rõ ràng, dùng icon sang trọng:
  💻 **Màn hình:** ...
  🧠 **CPU:** ...
  🎮 **GPU:** ...
  💾 **RAM & Lưu trữ:** ...
  🔋 **Pin & Màu sắc:** ...
  💵 **Giá bán:** ...
A. Nếu là tư vấn chung (ví dụ: "tư vấn laptop gaming", "laptop 20 triệu", "học lập trình nên mua máy nào"):
   - PHẢI liệt kê TẤT CẢ các máy trong dữ liệu theo đúng số thứ tự (Máy 1, Máy 2... hoặc 1. 2. 3...).
   - Với mỗi máy CHỈ trình bày:
     • STT
     • Tên máy
     • Giá
   - TUYỆT ĐỐI không liệt kê CPU, RAM, GPU, Storage nếu khách không yêu cầu.
   - KHÔNG được rút gọn danh sách, KHÔNG được viết "và các máy khác...", KHÔNG bỏ sót máy nào.

B. Nếu khách hỏi về một máy cụ thể:
   - Chỉ trả lời về đúng máy đó.
   - Trình bày đầy đủ cấu hình từ dữ liệu.

C. Nếu khách yêu cầu so sánh:
   - Nếu khách nói "so sánh máy 1 với máy 2" → dựa vào danh sách vừa trả lời trước đó để xác định đúng tên máy.
     Ví dụ: bạn vừa trả ra:
       1. Laptop Lenovo LOQ 15ARP9 – 22,690,000đ
       2. Laptop Lenovo LOQ 15AHP10 – 31,690,000đ
     → "so sánh 1 với 2" = so sánh LOQ 15ARP9 với LOQ 15AHP10.
   - Nếu không chỉ định → so sánh các máy cùng phân khúc giá trong dữ liệu.
   - KHI SO SÁNH: PHẢI nêu rõ ưu nhược điểm từng máy dựa trên cấu hình và giá cả.
   C. KHI KHÁCH YÊU CẦU SO SÁNH (VD: "So sánh 1 và 2"):
- Đối chiếu chuẩn xác [MÁY SỐ 1] và [MÁY SỐ 2].
- BẮT BUỘC DÙNG BẢNG MARKDOWN để so sánh các thông số. Ví dụ form bảng:
  | Tiêu chí | **[Tên máy 1 ngắn gọn]** | **[Tên máy 2 ngắn gọn]** |
  | :--- | :--- | :--- |
  | 💰 **Giá bán** | ... | ... |
  | 🧠 **CPU** | ... | ... |
  | 🎮 **GPU** | ... | ... |
  | 💻 **Màn hình** | ... | ... |
  | 🔋 **Pin & RAM** | ... | ... |

D. Nếu khách hỏi chi tiết cấu hình một máy:
   - Trình bày đầy đủ toàn bộ thông tin cấu hình từ dữ liệu của máy đó.

=====================
KIỂM TRA TRƯỚC KHI TRẢ LỜI
=====================
Trước khi gửi câu trả lời, hãy tự kiểm tra:
- [ ] Tôi đã liệt kê đủ số máy trong dữ liệu chưa? (đếm lại)
- [ ] Tôi có bỏ sót máy nào không?
- [ ] Tôi có thêm máy ngoài dữ liệu không?
- [ ] Tôi có bịa thêm thông tin cấu hình không?
Nếu vi phạm bất kỳ điều nào → sửa lại trước khi trả lời.
"""


def format_search_context(results: list[dict], indexed_results: list[tuple] = None) -> str:
    if not results:
        return "Không tìm thấy laptop phù hợp."

    lines = []
    items = indexed_results if indexed_results else [(None, r) for r in results]
    for idx, r in items:
        prefix = f"Máy {idx}:" if idx is not None else "-"
        lines.append(
            f"{prefix} {r['name']}\n"
            f"  CPU: {r['cpu']} | RAM: {r['ram']}GB | Storage: {r['storage']}GB\n"
            f"  GPU: {r['gpu']}\n"
            f"  Màn hình: {r['screen_size']} inch | {r['screen_resolution']} | {r['screen_panel']}\n"
            f"  Pin: {r['battery_wh']} Wh | Màu sắc: {r['color']}\n"
            f"  Giá: {r['price']:,.0f}đ | Rating: {r['rating']}/5\n"
            f"  Phản hồi từ người dùng: {r.get('review_text', 'Không có phản hồi')}\n"
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
        f"  Màn hình: {result['screen_size']} inch | {result['screen_resolution']} | {result['screen_panel']}\n"
        f"  Pin: {result['battery_wh']} Wh | Màu sắc: {result['color']}\n"
        f"  Giá: {result['price']:,.0f}đ | Rating: {result['rating']}/5\n"
        f"  Phản hồi từ người dùng: {result.get('review_text', 'Không có phản hồi')}\n"
        f"  Mô tả: {result['mo_ta']}"
    )


def ask_llm(user_query: str, context: str, history: list) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for h in history[-2:]:
        # Nhúng context của lượt trước vào user message
        prev_content = (
            f"--- Dữ liệu laptop tìm được ---\n{h['context']}\n\n"
            f"--- Câu hỏi của khách ---\n{h['user']}"
        ) if h.get("context") else h["user"]

        messages.append({"role": "user", "content": prev_content})
        messages.append({"role": "assistant", "content": h["assistant"]})

    messages.append({
        "role": "user",
        "content": (
            f"--- Dữ liệu laptop tìm được ---\n{context}\n\n"
            f"--- Câu hỏi của khách ---\n{user_query}"
        )
    })

    try:
        response = llm.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Xin lỗi, tôi gặp sự cố khi xử lý yêu cầu. Vui lòng thử lại. ({e})"



def extract_indices(query: str) -> list[int]:
    q = query.lower()

    ref_keywords = r'(?:máy|số|lap|laptop|cái|sản phẩm|sp)'
    matches = re.findall(rf'{ref_keywords}\s*([1-9][0-9]?)', q)
    if matches:
        return [int(x) for x in matches]

    action_keywords = ['so sánh', 'compare', 'chi tiết', 'thông số', 'detail', 'xem']
    if any(kw in q for kw in action_keywords):
        return [int(x) for x in re.findall(r'\b([1-9]|1[0-9]|20)\b', q)]

    return []


if __name__ == "__main__":
    model, collection = load_retriever()
    history = []
    session_products = {}

    print("=" * 60)
    print("TƯ VẤN LAPTOP AI | 'exit' để thoát")
    print("=" * 60)

    while True:
        query = input("Bạn: ").strip()
        if query.lower() == "exit":
            break
        if not query:
            continue

        indices = extract_indices(query)

        if indices and session_products:
            valid_pairs = [(i, session_products[i]) for i in indices if i in session_products]
            if not valid_pairs:
                context = "Không tìm thấy máy theo số thứ tự đó trong danh sách vừa tìm."
            elif len(valid_pairs) == 1:
                idx, r = valid_pairs[0]
                context = f"Máy {idx}:\n" + format_lookup_context(r)
            else:
                context = format_search_context(
                    [r for _, r in valid_pairs],
                    indexed_results=valid_pairs
                )

        elif is_direct_name(query) or is_lookup(query):
            result = lookup(query, model, collection)
            context = format_lookup_context(result)

        else:
            results, _ = search(query, model, collection, top_k=10)
            session_products = {i + 1: r for i, r in enumerate(results)}
            context = format_search_context(
                results,
                indexed_results=[(i + 1, r) for i, r in enumerate(results)]
            )

        answer = ask_llm(query, context, history)
        print(f"\n{answer}\n")

        history.append({"user": query, "assistant": answer})
