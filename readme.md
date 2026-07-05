# 🚀 Getting Started

Hello guys, if you read this text you are my close friend.

If you want start this project you need some **.env** keys.

---

## 1. Generate 3 Secret Keys

Go to:

**https://djecrety.ir**

Copy the generated key and paste it into:

```env
SECRET_KEY=
EMAIL_VERIFY_KEY=
FORGOT_PASSWORD_KEY=
```

---

## 2. Google App Password & Email

Write your email in:

```env
MAIL_APP_NAME=
```

Go to:

**https://myaccount.google.com/apppasswords**

Create a new App Password, copy it, and write it in:

```env
MAIL_APP_PASSWORD=
```

---

## ✅ Nice!

You are finish big part.

Now rename:

```text
example.env
```

to:

```text
.env
```

---

## 3. Install Requirements

If you use **github.com/LoLChC/Gits**, write this command in terminal:

```bash
gits req-load
```

If you don't use **Gits**, run:

```bash
pip install -r requirements.txt
```

---

## 4. Run the Project

Write this command in terminal:

```bash
python manage.py runserver
```
