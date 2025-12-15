import streamlit as st
from datetime import datetime, timedelta
import io
import os

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# =========================
# 0) 基本設定
# =========================
DEFAULT_PROVIDER_NAME = "高如慧"  # 乙方（你）
FONT_PATH = "assets/fonts/NotoSansTC-Regular.ttf"
FONT_NAME = "NotoSansTC"


# =========================
# 1) Page config
# =========================
st.set_page_config(
    page_title="廣告投放服務合約產生器",
    page_icon="📋",
    layout="centered"
)

st.title("📋 廣告投放服務合約")
st.markdown("---")


# =========================
# 2) Session State
# =========================
if "generated" not in st.session_state:
    st.session_state.generated = False
    st.session_state.client_message = ""
    st.session_state.payment_message = ""
    st.session_state.pdf_bytes = b""
    st.session_state.last_client_name = ""


# =========================
# 3) 字型嵌入
# =========================
def ensure_font_loaded():
    if not os.path.exists(FONT_PATH):
        st.error(f"找不到字型檔：{FONT_PATH}")
        st.stop()
    try:
        pdfmetrics.getFont(FONT_NAME)
    except KeyError:
        pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))


# =========================
# 4) 角色輸入（已翻正）
# =========================
st.header("🧾 甲方資訊（委託暨付款方）")
party_a_name = st.text_input(
    "甲方名稱（公司 / 客戶名稱）",
    placeholder="請輸入實際付款方名稱"
)

st.markdown("---")

st.header("👤 乙方資訊（服務執行者）")
party_b_name = st.text_input(
    "乙方名稱",
    value=DEFAULT_PROVIDER_NAME,
    disabled=True
)

st.markdown("---")


# =========================
# 5) 服務內容（展示用）
# =========================
st.header("服務內容說明")

st.markdown("""
**固定工作**
- 廣告上架  
- 廣告監控 / 維護 / 優化  
- 簡易週報（成果與優化方向）

**非固定工作**
- 廣告素材建議（依投放成效、競品、市場）
- 到達頁面優化建議（轉換異常時）
""")

st.warning("""
📌 提醒  
- 乙方為自然人，不開立統一發票。  
- 付款、帳務與稅務處理方式，由甲方依其自身規範與法令自行決定，乙方不提供稅務判斷。
""")

st.markdown("---")


# =========================
# 6) 收費方式
# =========================
st.header("💰 收費方式")

payment_option = st.radio(
    "請選擇付款方案：",
    ["17,000 元 / 月", "45,000 元 / 三個月"],
    index=0
)

st.markdown("---")


# =========================
# 7) 合作時間
# =========================
st.header("📅 合作時間")

default_start = datetime.now().date() + timedelta(days=7)
start_date = st.date_input(
    "合作啟動日期",
    value=default_start,
    min_value=datetime.now().date()
)

payment_day = None
payment_date = None

if payment_option == "17,000 元 / 月":
    payment_day = st.slider("每月付款日", 1, 28, 5)
    total_amount_text = "NT$17,000／月"
else:
    payment_date = st.date_input(
        "付款日期（建議於啟動前完成）",
        value=start_date - timedelta(days=3)
    )
    total_amount_text = "NT$45,000／三個月"

st.markdown("---")


# =========================
# 8) PDF 產生
# =========================
def generate_pdf_bytes():
    ensure_font_loaded()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )

    styles = {
        "title": ParagraphStyle("t", fontName=FONT_NAME, fontSize=18, alignment=1),
        "h": ParagraphStyle("h", fontName=FONT_NAME, fontSize=12, spaceBefore=12),
        "n": ParagraphStyle("n", fontName=FONT_NAME, fontSize=10, leading=16),
        "i": ParagraphStyle("i", fontName=FONT_NAME, fontSize=10, leftIndent=15, leading=16),
    }

    story = []
    story.append(Paragraph("<b>廣告投放服務合約書</b>", styles["title"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"<b>甲方（委託暨付款方）：</b>{party_a_name}", styles["n"]))
    story.append(Paragraph(f"<b>乙方（服務執行者）：</b>{party_b_name}", styles["n"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        f"本合約自 {start_date.strftime('%Y/%m/%d')} 起生效。",
        styles["n"]
    ))

    story.append(Paragraph("<b>服務內容</b>", styles["h"]))
    story.append(Paragraph("1. 廣告上架、監控與優化", styles["i"]))
    story.append(Paragraph("2. 定期成效摘要與優化方向說明", styles["i"]))

    story.append(Paragraph("<b>費用與付款</b>", styles["h"]))
    story.append(Paragraph(
        f"甲方應依約定支付服務費用：{total_amount_text}。",
        styles["n"]
    ))

    story.append(Paragraph("<b>付款方式與稅務責任</b>", styles["h"]))
    story.append(Paragraph(
        "乙方為自然人，不開立統一發票。付款方式、帳務與稅務申報，"
        "由甲方依自身狀況與相關法令自行決定並負責，乙方不提供稅務判斷。",
        styles["n"]
    ))

    story.append(Spacer(1, 20))
    story.append(Paragraph("甲方簽名：__________________", styles["n"]))
    story.append(Paragraph("乙方簽名：__________________", styles["n"]))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# =========================
# 9) 生成
# =========================
if st.button("📄 生成合約內容", type="primary", use_container_width=True):
    if not party_a_name.strip():
        st.error("請輸入甲方名稱（付款方）")
    else:
        st.session_state.pdf_bytes = generate_pdf_bytes()
        st.session_state.generated = True
        st.session_state.last_client_name = party_a_name
        st.success("✅ 已生成合約內容")


# =========================
# 10) 顯示區
# =========================
if st.session_state.generated:
    st.subheader("📥 下載合約 PDF")
    st.download_button(
        label="⬇️ 下載合約 PDF",
        data=st.session_state.pdf_bytes,
        file_name=f"廣告投放服務合約_{st.session_state.last_client_name}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

st.markdown("---")
st.caption("如有任何問題，請隨時與我聯繫。")
