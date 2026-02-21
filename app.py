from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'insight-nexus-secret-2026'

# ── CONFIG ──────────────────────────────────────────────
ADMIN_PASSWORD = 'Renewal3-Manhole3-Onscreen3-Immunity0-Backstab4'
UPLOAD_FOLDER  = 'static/uploads'
ALLOWED_EXTS   = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
DB_PATH        = 'blog.db'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ── DATABASE ─────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as db:
        db.executescript('''
            CREATE TABLE IF NOT EXISTS posts (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                title     TEXT    NOT NULL,
                category  TEXT    NOT NULL,
                excerpt   TEXT    NOT NULL,
                content   TEXT    NOT NULL,
                image_url TEXT,
                author    TEXT    DEFAULT 'Insight Nexus',
                created   TEXT    NOT NULL
            );
            CREATE TABLE IF NOT EXISTS comments (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id    INTEGER NOT NULL,
                author     TEXT    NOT NULL,
                text       TEXT    NOT NULL,
                created    TEXT    NOT NULL,
                FOREIGN KEY (post_id) REFERENCES posts(id)
            );
        ''')

init_db()

# ── HELPERS ──────────────────────────────────────────────
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTS

# ── PUBLIC ROUTES ─────────────────────────────────────────

@app.route('/')
def home():
    q    = request.args.get('q', '').strip()
    cat  = request.args.get('category', 'All')
    db   = get_db()

    query = 'SELECT * FROM posts WHERE 1=1'
    params = []

    if q:
        query  += ' AND (title LIKE ? OR excerpt LIKE ? OR content LIKE ?)'
        params += [f'%{q}%', f'%{q}%', f'%{q}%']
    if cat and cat != 'All':
        query  += ' AND category = ?'
        params.append(cat)

    query += ' ORDER BY id DESC'
    posts = db.execute(query, params).fetchall()

    categories = ['All'] + [r['category'] for r in
                  db.execute('SELECT DISTINCT category FROM posts ORDER BY category').fetchall()]
    db.close()
    return render_template('home.html', posts=posts, categories=categories,
                           q=q, selected_cat=cat)


@app.route('/blog')
def blog():
    db    = get_db()
    cat   = request.args.get('category', 'All')
    query = 'SELECT * FROM posts'
    params = []
    if cat != 'All':
        query += ' WHERE category = ?'
        params.append(cat)
    query += ' ORDER BY id DESC'
    posts = db.execute(query, params).fetchall()
    categories = ['All'] + [r['category'] for r in
                  db.execute('SELECT DISTINCT category FROM posts ORDER BY category').fetchall()]
    db.close()
    return render_template('blog.html', posts=posts, categories=categories, selected_cat=cat)


@app.route('/post/<int:post_id>')
def post(post_id):
    db       = get_db()
    p        = db.execute('SELECT * FROM posts WHERE id=?', (post_id,)).fetchone()
    comments = db.execute('SELECT * FROM comments WHERE post_id=? ORDER BY id DESC', (post_id,)).fetchall()
    db.close()
    if not p:
        return redirect(url_for('home'))
    return render_template('post.html', post=p, comments=comments)


@app.route('/post/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    author  = request.form.get('author', '').strip()
    text    = request.form.get('text', '').strip()
    if author and text:
        db = get_db()
        db.execute('INSERT INTO comments (post_id, author, text, created) VALUES (?,?,?,?)',
                   (post_id, author, text, datetime.now().strftime('%B %d, %Y')))
        db.commit()
        db.close()
    return redirect(url_for('post', post_id=post_id) + '#comments')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


# ── ADMIN ROUTES ──────────────────────────────────────────

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        pwd = request.form.get('password', '')
        if pwd == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin'))
        flash('Wrong password.')
    return render_template('signin.html')


@app.route('/signout')
def signout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect(url_for('signin'))
    db    = get_db()
    posts = db.execute('SELECT * FROM posts ORDER BY id DESC').fetchall()
    db.close()
    return render_template('admin.html', posts=posts)


@app.route('/admin/new', methods=['GET', 'POST'])
def new_post():
    if not session.get('admin'):
        return redirect(url_for('signin'))

    if request.method == 'POST':
        title    = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        excerpt  = request.form.get('excerpt', '').strip()
        content  = request.form.get('content', '').strip()
        img_url  = request.form.get('image_url', '').strip()

        # Handle file upload
        file = request.files.get('image_file')
        if file and file.filename and allowed_file(file.filename):
            fname   = secure_filename(file.filename)
            fname   = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{fname}"
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
            img_url = url_for('static', filename=f'uploads/{fname}')

        if title and category and excerpt and content:
            db = get_db()
            db.execute('''INSERT INTO posts (title, category, excerpt, content, image_url, created)
                          VALUES (?,?,?,?,?,?)''',
                       (title, category, excerpt, content, img_url,
                        datetime.now().strftime('%B %d, %Y')))
            db.commit()
            db.close()
            flash('Blog post published!')
            return redirect(url_for('admin'))
        flash('Please fill all required fields.')

    return render_template('new_post.html')


@app.route('/admin/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if not session.get('admin'):
        return redirect(url_for('signin'))
    db = get_db()
    db.execute('DELETE FROM comments WHERE post_id=?', (post_id,))
    db.execute('DELETE FROM posts WHERE id=?', (post_id,))
    db.commit()
    db.close()
    flash('Post deleted.')
    return redirect(url_for('admin'))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
