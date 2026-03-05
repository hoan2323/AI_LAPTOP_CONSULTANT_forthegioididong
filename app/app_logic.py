import gradio as gr
import re
import sys, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))          
FOLDER_C = os.path.abspath(os.path.join(BASE_DIR, "../rag"))   

sys.path.insert(0, FOLDER_C)
from search import load_retriever, search, lookup, is_direct_name, is_lookup 
from llm import ask_llm, format_search_context, format_lookup_context, extract_indices 

print("Đang khởi động giao diện, kết nối Database và LLM...")
embed_model, vector_db = load_retriever()

# =========================
# BƯỚC 1: RENDER KẾT QUẢ RA HTML
# =========================
def render_html_results(results):
    if not results:
        return "" 
    html_output = '<div class="result-grid">'
    for r in results:
        price_fmt = "{:,.0f}".format(r.get('price', 0)).replace(",", ".")
        name = str(r.get('name', 'Unknown'))
        
        def clean_val(val):
            v = str(val).strip()
            return "" if v.lower() in ['nan', 'none', 'null', ''] else v

        cpu = clean_val(r.get('cpu', '')) or 'Đang cập nhật'
        gpu = clean_val(r.get('gpu', '')) or 'Đang cập nhật'
        ram = f"{clean_val(r.get('ram', ''))}GB" if clean_val(r.get('ram', '')) else "Đang cập nhật"
        storage = f"{clean_val(r.get('storage', ''))}GB" if clean_val(r.get('storage', '')) else "Đang cập nhật"
        sim_score = round(r.get('similarity', 0), 3) if isinstance(r.get('similarity', 0), float) else 0

        screen_size = clean_val(r.get('screen_size', ''))
        screen_res = clean_val(r.get('screen_resolution', ''))
        screen_panel = clean_val(r.get('screen_panel', ''))
        screen_parts = [p for p in [f"{screen_size} inch" if screen_size else "", screen_res, screen_panel] if p]
        screen_display = ", ".join(screen_parts) if screen_parts else "Đang cập nhật"

        battery_display = f"{clean_val(r.get('battery_wh', ''))} Wh" if clean_val(r.get('battery_wh', '')) else "Đang cập nhật"
        color_display = clean_val(r.get('color', '')) or "Đang cập nhật"
        rating_display = clean_val(r.get('rating', '')) or "Chưa có"

        review_text_raw = str(r.get('review_text', ''))
        reviews_html = ""
        if review_text_raw.lower() in ['nan', 'none', 'null', '']:
            reviews_html = "<div class='review-item' style='border-left-color: #565869; font-style: italic; color: #888;'>Chưa có đánh giá chi tiết từ người dùng.</div>"
        else:
            for rev in [rev.strip() for rev in review_text_raw.split('||') if rev.strip()]:
                reviews_html += f"<div class='review-item'><i class='fas fa-user-circle'></i> {rev}</div>"

        card_html = f"""
        <div class="card-wrapper">
            <div class="laptop-card">
                <div class="card-header">
                    <div class="laptop-name">{name}</div>
                    <div class="laptop-price">{price_fmt} ₫</div>
                </div>
                <div class="badges">
                    <span class="badge badge-cpu"><i class="fas fa-microchip"></i> {cpu}</span>
                    <span class="badge badge-gpu"><i class="fas fa-gamepad"></i> {gpu}</span>
                </div>
                <div class="specs-row">
                    <div class="spec-item"><i class="fas fa-memory"></i> <span>{ram}</span></div>
                    <div class="spec-item"><i class="fas fa-hdd"></i> <span>{storage}</span></div>
                </div>
                <div class="card-detail" style="display: none;">
                    <div class="detail-section">
                        <div class="detail-title">⚙️ Cấu hình chi tiết</div>
                        <ul class="specs-list">
                            <li><b>CPU:</b> <span>{cpu}</span></li>
                            <li><b>RAM:</b> <span>{ram}</span></li>
                            <li><b>GPU:</b> <span>{gpu}</span></li>
                            <li><b>Ổ cứng:</b> <span>{storage}</span></li>
                            <li><b>Màn hình:</b> <span>{screen_display}</span></li>
                            <li><b>Pin:</b> <span>{battery_display}</span></li>
                            <li><b>Màu sắc:</b> <span>{color_display}</span></li>
                        </ul>
                    </div>
                    <div class="detail-section">
                        <div class="detail-title">⭐ Đánh giá ({rating_display} Sao)</div>
                        <div class="reviews-container">{reviews_html}</div>
                    </div>
                </div>
                <button class="view-detail-btn" onclick="toggleDetail(this)">Xem chi tiết</button>
            </div>
        </div>"""
        html_output += card_html
    html_output += '</div>'
    return html_output

def smart_combine(memory, new_query):
    if not memory: return new_query
    mem = memory
    new_lower = new_query.lower()
    if re.search(r'\d+\s*(tr|triệu|m)', new_lower):
        mem = re.sub(r"(?:dưới|tầm|khoảng|trên|từ|max|min|tối đa|ít nhất)?\s*\d+(?:[.,]\d+)?\s*(?:tr|triệu|m)(?:\s*(?:-|đến|tới)\s*\d+(?:[.,]\d+)?\s*(?:tr|triệu|m))?", "", mem, flags=re.IGNORECASE)
    if re.search(r'(ram\s*\d+|\d+\s*gb)', new_lower):
        mem = re.sub(r"(?:ram\s*\d+|\d+\s*gb\s*ram|\d+\s*gb)", "", mem, flags=re.IGNORECASE)
    if re.search(r'(ssd|tb)', new_lower):
        mem = re.sub(r"(?:\d+\s*tb\s*ssd|ssd\s*\d+\s*tb|ssd|\d+\s*tb)", "", mem, flags=re.IGNORECASE)
    if re.search(r'(i\d|ryzen\s*\d)', new_lower):
        mem = re.sub(r"(core\s+)?(i3|i5|i7|i9)|(ryzen\s*\d)", "", mem, flags=re.IGNORECASE)
    categories = r"(gaming|game|chơi game|văn phòng|office|đồ họa|thiết kế|render|mỏng nhẹ|sinh viên|code|lập trình)"
    if re.search(categories, new_lower): mem = re.sub(categories, "", mem, flags=re.IGNORECASE)
    brands = r"(apple|macbook|mac|dell|hp|asus|lenovo|acer|msi|samsung|gigabyte|thinkpad|legion|rog|tuf|vivobook|ideapad)"
    if re.search(brands, new_lower): mem = re.sub(brands, "", mem, flags=re.IGNORECASE)
    if "laptop" in new_lower: mem = re.sub(r"laptop", "", mem, flags=re.IGNORECASE)
    return re.sub(r'\s+', ' ', f"{mem} {new_query}".strip())

# =========================
# BƯỚC 3: HÀM CHAT TỔNG 
# =========================
def chat_logic(new_query, memory, chat_history, ui_history, current_results):
    if not new_query.strip():
        return gr.skip()
    
    has_results = False
    html_res = ""
    llm_context = ""
    new_memory = memory
    new_current_results = current_results # Kế thừa danh sách máy trên màn hình

    # 1. BẮT ĐẠI TỪ CHỈ ĐỊNH ("chi tiết con 1", "so sánh 1 và 2", "hỏi thêm con 3")
    indices = extract_indices(new_query)
    
    if indices and current_results:
        # Bốc đúng máy từ UI ra để render lên màn hình
        valid_results = [current_results[i-1] for i in indices if 1 <= i <= len(current_results)]
        
        if valid_results:
            has_results = True
            # Chỉ hiển thị thẻ máy được gọi trên giao diện Web
            html_res = render_html_results(valid_results)
            
            # ĐÃ FIX: TRUYỀN TOÀN BỘ 6 MÁY CHO LLM ĐỌC
            # Bằng cách này, AI sẽ luôn nhìn thấy đủ từ [MÁY SỐ 1] đến [MÁY SỐ 6] 
            # để tự đối chiếu chính xác khi bạn hỏi "con 3", "con 4"
            llm_context = format_search_context(current_results)

    # 2. NẾU KHÔNG GỌI SỐ THỨ TỰ -> CHẠY TÌM KIẾM MỚI BÌNH THƯỜNG
    if not has_results:
        combined_query = smart_combine(memory, new_query)
        
        def do_search(query):
            if is_direct_name(query) or is_lookup(query):
                res = lookup(query, embed_model, vector_db)
                if res:
                    return True, render_html_results([res]), format_lookup_context(res), [res]
            else:
                res_list, _ = search(query, embed_model, vector_db, top_k=6)
                if res_list:
                    return True, render_html_results(res_list), format_search_context(res_list), res_list
            return False, "", "Không tìm thấy laptop phù hợp.", []

        has_results, html_res, llm_context, temp_results = do_search(combined_query)
        if has_results:
            new_memory = combined_query
            new_current_results = temp_results # Lưu lại danh sách máy mới vào State
        elif memory: 
            has_results, html_res, llm_context, temp_results = do_search(new_query)
            if has_results:
                new_memory = new_query
                new_current_results = temp_results

    # 3. CHUYỂN QUA CHO LLM TRẢ LỜI
    bot_response = ask_llm(new_query, llm_context, chat_history)

    chat_history.append({"user": new_query, "assistant": bot_response})
    ui_history.append({"role": "user", "content": new_query})
    ui_history.append({"role": "assistant", "content": bot_response})

    if has_results:
        res_col_update = gr.update(visible=True)
        chat_col_update = gr.update(elem_classes=["chat-col", "side"])
    else:
        res_col_update = gr.update(visible=False)
        chat_col_update = gr.update(elem_classes=["chat-col", "center"])

    hero_update = gr.update(visible=False)
    chatbot_update = gr.update(visible=True)
    clear_btn_update = gr.update(visible=True)

    return html_res, new_memory, chat_history, ui_history, new_current_results, "", res_col_update, chat_col_update, hero_update, chatbot_update, clear_btn_update


def reset_all():
    return "", "", [], [], [], "", gr.update(visible=False), gr.update(elem_classes=["chat-col", "center"]), gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)