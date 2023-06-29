async def get_html_template(user_phone, post_text, photo_link):
    email_template = f'''
    <!DOCTYPE html>
    <html lang="ru">
       <head>
          <meta charset="UTF-8">
          <title>Новый пользователь в боте</title>
       </head>
       <body>
          <h1>Пользователь заинтересовался постом</h1>
          <h2>
            Пользователь с номером телефона {user_phone} заинтересовался данным постом:
          </h2><br>
          <p>
          {post_text}
          </p><br>
          <img src="{photo_link}" alt="Не удалось загрузить фотографию поста">
       </body>
    </html>
    '''

    return email_template
