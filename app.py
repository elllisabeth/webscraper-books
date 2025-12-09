import streamlit as st
import pandas as pd
import json
import requests
from bs4 import BeautifulSoup

# ----------------------------
# Scraper Function
# ----------------------------
def scrape_books():
    base_url = "https://books.toscrape.com/catalogue/page-{}.html"
    book_list = []

    for page in range(1, 51):  # Loop all 50 pages
        url = base_url.format(page)
        response = requests.get(url)

        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, "html.parser")
        books = soup.find_all("article", class_="product_pod")

        for book in books:
            title = book.h3.a["title"]
            price = book.find("p", class_="price_color").text.replace("Â", "")
            rating = book.p["class"][1]
            stock = book.find("p", class_="instock availability").text.strip()
            image_url = "https://books.toscrape.com/catalogue/" + \
                        book.img["src"].replace("../../", "")

            book_list.append({
                "title": title,
                "price": price,
                "rating": rating,
                "stock": stock,
                "image_url": image_url
            })

    df = pd.DataFrame(book_list)
    return df


# ----------------------------
# Streamlit UI
# ----------------------------
st.set_page_config(page_title="Book Scraper Automation", layout="wide")

st.markdown("<h1 style='text-align: center; color: white;'>📚 Book Scraper Automation</h1>",
            unsafe_allow_html=True)
st.write("Click button below to scrape data and display results.")

if st.button("🔍 Run Scraper"):
    df = scrape_books()
    st.success("Scraping completed!")

    # Filter Rating
    rating_filter = st.selectbox("Filter by rating:",
                                 ["All", "One", "Two", "Three", "Four", "Five"])
    if rating_filter != "All":
        df = df[df["rating"] == rating_filter]

    # Search Bar
    search_query = st.text_input("Search book title:")
    if search_query:
        df = df[df["title"].str.contains(search_query, case=False)]

    # Show image thumbnails
    df_display = df.copy()
    df_display["image"] = df_display["image_url"].apply(
        lambda x: f'<img src="{x}" width="60">'
    )

    # Pagination setup
    items_per_page = 50
    total_items = len(df_display)
    total_pages = (total_items // items_per_page) + 1

    page = st.number_input(
        "Select Page:",
        min_value=1,
        max_value=total_pages,
        step=1
    )

    start_row = (page - 1) * items_per_page
    end_row = start_row + items_per_page
    paginated_df = df_display.iloc[start_row:end_row]

    st.write(f"📚 Showing page {page} of {total_pages}")
    st.markdown(
        paginated_df.to_html(escape=False),
        unsafe_allow_html=True
    )


    # Save filtered data to JSON
    df.to_json("books.json", orient="records", indent=4)

    with open("books.json", "rb") as f:
        st.download_button(
            label="📥 Download JSON",
            data=f,
            file_name="books.json",
            mime="application/json"
        )

# Footer
st.markdown(
    "<br><p style='text-align: center; color: gray;'>Built with ❤️ using Streamlit</p>",
    unsafe_allow_html=True
)