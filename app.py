import streamlit as st
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import io

# ========= 字體設定（內建中文） =========
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
FONT_NAME = 'STSong-Light'

# ========= 基本資料（請填） =========
PROVIDER_NAME = "（請填你的姓名）"
BANK_NAME = "中國信託商業銀行"
BANK_CODE = "822"
ACCOUNT_NUMBER = "783540208870"

# ========= 頁面設定 =========
st.set_page_config(
    page_title="廣告投放服務選擇",
    page_icon="📋",
    layout="centered"
)

st.title("📋 廣告投放服務內容")
st.markdown("---")

# ========= 服務內容 =========
st.header("服務內容說明")

st.subheader("✅ 固定工作")
st.markdown("""
- 廣告上架  
- 廣告監控 / 維護 / 優化  
- 簡易週報（成果與優化方向）
""")

st.subheader("📌 非固定工作")
st.markdown("""
- 廣告素材建議（依成效、競品、市場）
- 到達頁面優化建議（轉換率異常時）
""")

st.warning("""
📌 提醒：本人以自然人身分提供服務，不開立統一發票。  
付款方式與稅務處理將由客戶依自身帳務與法規自行決定，甲方不提供稅務判斷。
""")

st.markdown("---")

# ========= 收費方式 =========
st.header("💰 收費方式")

payment_option = st.radio(
    "請選擇付款方案：",
    ["17,000 元 / 月", "45,000 元 / 三個月"],
    index=0
)

st.markdown("---")

# ========= 合作時間 =========
st.header("📅 合作時間")

default_start = datetime.now().date() + timedelta(days=7)
start_date = st.date_input(
    "合作啟動日期",
    value=default_start,
    min_value=datetime.now().date()
)

if payment_option == "17,000 元 / 月":
    payment_day = st.slider("每月付款日", 1, 28, 5)
    total_amount = "NT$17,000 / 月"
    contract_months = 1
else:
    payment_date = st.date_input(
        "付款日期（建議於啟動前完成）",
        value=start_date - timedelta(days=3),
        min_value=datetime.now().date(),
        max_value=start_date
    )
    total_amount = "NT$45,000 / 三個月"
    contract_months = 3

st.markdown("---")

# ========= 客戶資訊 =========
st.header("📝 客戶資訊")
client_name = st.text_input("客戶名稱 / 公司名稱", placeholder="請輸入")

st.markdown("---")

# ========= 生成 =========
if st.button("📄 生成合約與付款資訊", type="primary", use_container_width=True):
    if not client_name or not PROVIDER_NAME:
        st.error("請確認已填寫『甲方名稱』與『客戶名稱』")
    else:
        st.success("✅ 已生成")

        # ---- 客戶回傳訊息 ----
        st.subheader("📤 請客戶回傳以下訊息")

        if payment_option == "17,000 元 / 月":
            client_message = f"""
我已確認合作內容：

【客戶名稱】{client_name}
【付款方案】17,000 元 / 月
【合作啟動日】{start_date.strftime('%Y/%m/%d')}
【每月付款日】每月 {payment_day} 日
"""
        else:
            client_message = f"""
我已確認合作內容：

【客戶名稱】{client_name}
【付款方案】45,000 元 / 三個月
【合作啟動日】{start_date.strftime('%Y/%m/%d')}
【付款日期】{payment_date.strftime('%Y/%m/%d')}
"""

        st.code(client_message)
        st.markdown("---")

        # ---- 付款資訊 ----
        st.subheader("💳 付款資訊")
        st.markdown(f"**應付金額：{total_amount}**")
        st.code(f"銀行：{BANK_NAME}（{BANK_CODE}）\n帳號：{ACCOUNT_NUMBER}")

        st.markdown("---")

        # ========= PDF 產生 =========
        def generate_pdf():
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
                "title": ParagraphStyle("t", fontName=FONT_NAME, fontSize=18, alignment=1, spaceAfter=20),
                "h": ParagraphStyle("h", fontName=FONT_NAME, fontSize=12, spaceBefore=12),
                "n": ParagraphStyle("n", fontName=FONT_NAME, fontSize=10, leading=16),
                "i": ParagraphStyle("i", fontName=FONT_NAME, fontSize=10, leftIndent=15, leading=16),
            }

            story = []
            story.append(Paragraph("<b>廣告投放服務合約書</b>", styles["title"]))

            end_date = start_date + timedelta(days=contract_months * 30)

            story.append(Paragraph(f"<b>甲方：</b>{PROVIDER_NAME}", styles["n"]))
            story.append(Paragraph(f"<b>乙方：</b>{client_name}", styles["n"]))
            story.append(Spacer(1, 10))

            story.append(Paragraph(
                f"合約期間：自 {start_date.strftime('%Y/%m/%d')} 起至 {end_date.strftime('%Y/%m/%d')} 止。",
                styles["n"]
            ))

            story.append(Paragraph("<b>服務內容</b>", styles["h"]))
            story.append(Paragraph("1. 廣告上架、監控、優化", styles["i"]))
            story.append(Paragraph("2. 週報與成效說明", styles["i"]))
            story.append(Paragraph("3. 素材與頁面優化建議（視需要）", styles["i"]))

            story.append(Paragraph("<b>費用</b>", styles["h"]))
            story.append(Paragraph(f"{total_amount}", styles["n"]))

            story.append(Paragraph("<b>付款方式與稅務責任</b>", styles["h"]))
            story.append(Paragraph(
                "甲方為自然人，不開立統一發票。付款方式、帳務與稅務申報，均由乙方依自身狀況及法規自行決定並負責。"
                "甲方僅配合提供必要收款文件，不負稅務判斷責任。",
                styles["n"]
            ))

            story.append(Spacer(1, 20))
            story.append(Paragraph("甲方簽名：______________", styles["n"]))
            story.append(Paragraph("乙方簽名：______________", styles["n"]))

            doc.build(story)
            buffer.seek(0)
            return buffer

        pdf = generate_pdf()
        st.download_button(
            "⬇️ 下載合約 PDF",
            data=pdf,
            file_name=f"廣告投放服務合約_{client_name}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

st.markdown("---")
st.caption("如有任何問題，請隨時聯繫。")
