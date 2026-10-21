import random
import streamlit as st
import chess

st.set_page_config(page_title="Cờ Vua | Royal Clash", page_icon="♟️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=Inter:wght@400;500;700;800&display=swap');
.stApp { background: radial-gradient(circle at top, #253c35 0%, #101916 45%, #090d0c 100%); color: #f6f0df; }
.block-container { max-width: 1100px; padding-top: 2rem; }
h1,h2,h3,p,div,span,label { font-family: Inter, sans-serif; }
.hero { text-align:center; padding: 5rem 1rem 3rem; border: 1px solid #b99755; border-radius: 28px; background: linear-gradient(135deg,rgba(31,53,45,.96),rgba(12,20,17,.96)); box-shadow: 0 20px 70px #0008; }
.hero h1 { font-family:'Playfair Display',serif; font-size: clamp(3rem,8vw,6rem); letter-spacing:.08em; color:#e9c778; margin:0; }
.hero p { color:#d4d0c3; font-size:1.1rem; letter-spacing:.12em; }
.stButton > button { border:1px solid #c8a45d; border-radius:12px; background:linear-gradient(135deg,#e6c574,#b58a3c); color:#172019; font-weight:800; min-height:2.8rem; transition:all .18s ease; }
.stButton > button:hover { border-color:#fff0b8; transform:translateY(-2px); box-shadow:0 8px 24px #0005; color:#101712; }
.board { display:grid; grid-template-columns:repeat(8,minmax(0,1fr)); border:5px solid #c5a15b; border-radius:10px; overflow:hidden; box-shadow:0 18px 45px #0008; }
.square { aspect-ratio:1; display:flex; align-items:center; justify-content:center; font-size:clamp(1.3rem,4vw,3rem); }
.light { background:#eadfc5; } .dark { background:#607c69; }
.smallnote { color:#c7c6b9; font-size:.9rem; }
</style>
""", unsafe_allow_html=True)

PIECES = {
    "K":"♔","Q":"♕","R":"♖","B":"♗","N":"♘","P":"♙",
    "k":"♚","q":"♛","r":"♜","b":"♝","n":"♞","p":"♟"
}

def init_game():
    st.session_state.board = chess.Board()
    st.session_state.selected = None
    st.session_state.screen = "game"
    st.session_state.mode = st.session_state.get("chosen_mode", "ai")
    st.session_state.message = ""

if "screen" not in st.session_state:
    st.session_state.screen = "home"
if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "selected" not in st.session_state:
    st.session_state.selected = None
if "mode" not in st.session_state:
    st.session_state.mode = "ai"

def end_message(board):
    if board.is_checkmate():
        winner = "Trắng" if board.turn == chess.BLACK else "Đen"
        return f"Chiếu hết! {winner} thắng."
    if board.is_stalemate():
        return "Hòa cờ: hết nước đi hợp lệ."
    if board.is_insufficient_material():
        return "Hòa cờ: không đủ quân để chiếu hết."
    if board.can_claim_draw():
        return "Có thể yêu cầu hòa."
    return ""

def ai_move():
    board = st.session_state.board
    if board.is_game_over():
        return
    legal = list(board.legal_moves)
    captures = [m for m in legal if board.is_capture(m)]
    checks = [m for m in legal if board.gives_check(m)]
    choices = checks or captures or legal
    board.push(random.choice(choices))
    st.session_state.selected = None

def show_board():
    board = st.session_state.board
    files = "abcdefgh"
    st.markdown('<div class="smallnote">Chọn quân của bên đang đi, sau đó chọn ô đích. Quân Trắng đi trước.</div>', unsafe_allow_html=True)
    for rank in range(7, -1, -1):
        cols = st.columns(8, gap="small")
        for file_idx in range(8):
            sq = chess.square(file_idx, rank)
            piece = board.piece_at(sq)
            symbol = PIECES[piece.symbol()] if piece else "　"
            is_light = (file_idx + rank) % 2 == 1
            bg = "#eadfc5" if is_light else "#607c69"
            selected = st.session_state.selected == sq
            legal_targets = []
            if st.session_state.selected is not None:
                legal_targets = [m.to_square for m in board.legal_moves if m.from_square == st.session_state.selected]
            if selected:
                bg = "#e5bb54"
            elif sq in legal_targets:
                bg = "#a7bd70" if not piece else "#d38b69"
            label = f"{symbol}"
            if file_idx == 0:
                label += f"\\n{rank+1}"
            if rank == 0:
                label += f"\\n{files[file_idx]}"
            with cols[file_idx]:
                clicked = st.button(label, key=f"sq_{sq}_{board.ply()}", use_container_width=True)
                st.markdown(f"""<style>
                div[data-testid="stButton"] button[kind="secondary"] {{ background:{bg}; color:{'#ffffff' if piece and piece.color == chess.BLACK else '#172019'}; border:0; border-radius:0; min-height:clamp(42px,7vw,82px); padding:0; font-size:clamp(1.1rem,3.2vw,2.4rem); white-space:pre-line; line-height:1.1; }}
                </style>""", unsafe_allow_html=True)
                if clicked:
                    handle_square(sq)
                    st.rerun()

def handle_square(sq):
    board = st.session_state.board
    if board.is_game_over():
        return
    # In AI mode, player controls White only.
    if st.session_state.mode == "ai" and board.turn == chess.BLACK:
        return
    selected = st.session_state.selected
    piece = board.piece_at(sq)
    if selected is None:
        if piece and piece.color == board.turn:
            st.session_state.selected = sq
        return
    move = chess.Move(selected, sq)
    # Promote automatically to queen when a pawn reaches last rank.
    moving_piece = board.piece_at(selected)
    if moving_piece and moving_piece.piece_type == chess.PAWN and chess.square_rank(sq) in (0, 7):
        move = chess.Move(selected, sq, promotion=chess.QUEEN)
    if move in board.legal_moves:
        board.push(move)
        st.session_state.selected = None
        if st.session_state.mode == "ai" and not board.is_game_over():
            ai_move()
    elif piece and piece.color == board.turn:
        st.session_state.selected = sq
    else:
        st.session_state.selected = None

if st.session_state.screen == "home":
    st.markdown("""
    <div class="hero">
      <div style="font-size:4rem">♜ ♞ ♝ ♛ ♚ ♝ ♞ ♜</div>
      <h1>CỜ VUA</h1>
      <p>CHIẾN THUẬT · TRÍ TUỆ · VINH QUANG</p>
      <div style="font-size:1.2rem;color:#e9c778">ROYAL CLASH</div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    _, center, _ = st.columns([1,2,1])
    with center:
        if st.button("♟  CHƠI NGAY", use_container_width=True):
            st.session_state.screen = "mode"
            st.rerun()
    st.caption("Một bàn cờ. Hai bộ óc. Một chiến thắng.")
elif st.session_state.screen == "mode":
    st.markdown("<h1 style='text-align:center;color:#e9c778'>CHỌN CHẾ ĐỘ</h1>", unsafe_allow_html=True)
    st.write("")
    left, right = st.columns(2)
    with left:
        st.markdown("<div class='hero'><div style='font-size:3rem'>🤖</div><h2>ĐẤU VỚI AI</h2><p>Đối đầu máy tính</p></div>", unsafe_allow_html=True)
        if st.button("CHỌN ĐẤU VỚI AI", use_container_width=True):
            st.session_state.chosen_mode = "ai"
            init_game()
            st.rerun()
    with right:
        st.markdown("<div class='hero'><div style='font-size:3rem'>♟️</div><h2>HAI NGƯỜI CHƠI</h2><p>Luân phiên trên cùng thiết bị</p></div>", unsafe_allow_html=True)
        if st.button("CHỌN HAI NGƯỜI", use_container_width=True):
            st.session_state.chosen_mode = "local"
            init_game()
            st.rerun()
    if st.button("← Về trang đầu"):
        st.session_state.screen = "home"
        st.rerun()
else:
    board = st.session_state.board
    left, right = st.columns([3,1])
    with left:
        st.markdown("<h1 style='color:#e9c778'>♟ ROYAL CLASH</h1>", unsafe_allow_html=True)
        st.write("Chế độ: " + ("Đấu với AI" if st.session_state.mode == "ai" else "Hai người chơi"))
        show_board()
    with right:
        st.markdown("### BẢNG ĐIỀU KHIỂN")
        turn = "Trắng" if board.turn == chess.WHITE else "Đen"
        st.info(f"Đến lượt: **{turn}**")
        if board.is_check():
            st.warning("⚠️ Chiếu!")
        result = end_message(board)
        if result:
            st.success(result)
        st.markdown("#### Lịch sử nước đi")
        if board.move_stack:
            for i in range(0, len(board.move_stack), 2):
                white = board.san(board.move_stack[i]) if False else ""
            # Render SAN from a replayed board.
            replay = chess.Board()
            rows = []
            for i, move in enumerate(board.move_stack):
                san = replay.san(move)
                replay.push(move)
                if i % 2 == 0:
                    rows.append(f"{i//2+1}. {san}")
                else:
                    rows[-1] += f"   {san}"
            st.code("\n".join(rows[-10:]))
        else:
            st.caption("Chưa có nước đi nào.")
        if st.button("↻ Chơi lại", use_container_width=True):
            init_game()
            st.rerun()
        if st.button("⌂ Về trang đầu", use_container_width=True):
            st.session_state.screen = "home"
            st.rerun()
        if st.button("Chọn chế độ khác", use_container_width=True):
            st.session_state.screen = "mode"
            st.rerun()
