import streamlit as st

def inject_base_css():
    """
    Injects shared CSS styles for animation, layout, and interactivity across the Streamlit app.
    """
    st.markdown("""
    <style>
    /* Fade-in animation */
    .fade-in {
        animation: fadeIn 1.5s ease-in;
    }
    @keyframes fadeIn {
        0% {opacity: 0;}
        100% {opacity: 1;}
    }

    /* Floating nav/help button */
    .floating-button {
        position: fixed;
        bottom: 30px;
        right: 30px;
        background-color: #4F8A8B;
        color: white;
        padding: 0.75rem 1.25rem;
        border-radius: 30px;
        text-align: center;
        font-weight: bold;
        text-decoration: none;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
        transition: background-color 0.3s ease;
        z-index: 9999;
    }
    .floating-button:hover {
        background-color: #3b6e6e;
    }

    /* Info cards */
    .card {
        background-color: #F0F2F6;
        padding: 1rem;
        border-radius: 10px;
        transition: box-shadow 0.3s ease;
    }
    .card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    /* Consistent heading spacing */
    h2 {
        margin-top: 2rem;
    }

    /* Banner image (short, full width) */
    .banner {
        width: 100%;
        height: 200px;
        object-fit: cover;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)