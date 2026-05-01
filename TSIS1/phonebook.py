import psycopg2
import json
import csv
from config import params

def get_conn():
    return psycopg2.connect(**params)

def import_from_json(filename="contacts.json"):
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                with open(filename, "r", encoding="utf-8") as f:
                    contacts = json.load(f)
                
                for c in contacts:
                    cur.execute("SELECT id FROM contacts WHERE name = %s", (c['name'],))
                    exists = cur.fetchone()
                    
                    if exists:
                        choice = input(f"Контакт {c['name']} уже существует. Перезаписать (y) или пропустить (n)? ").lower()
                        if choice != 'y':
                            continue
                        cur.execute("DELETE FROM contacts WHERE name = %s", (c['name'],))
                    

                    cur.execute(
                        "INSERT INTO contacts (name, email, birthday) VALUES (%s, %s, %s)",
                        (c['name'], c['email'], c.get('birth') or c.get('birthday'))
                    )
                    

                    if c.get('group'):
                        cur.execute("CALL move_to_group(%s, %s)", (c['name'], c['group']))
                    if c.get('phones'):
                        phone_list = c['phones'].split(',')
                        for p in phone_list:
                            cur.execute("CALL add_phone(%s, %s, %s)", (c['name'], p.strip(), 'mobile'))
                conn.commit()
                print("Импорт из JSON завершен.")
    except FileNotFoundError:
        print(f"Файл {filename} не найден.")
    except Exception as e:
        print(f"Ошибка при импорте JSON: {e}")


def import_from_csv(filename="contacts.csv"):
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                with open(filename, mode='r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        cur.execute("""
                            INSERT INTO contacts (name, email, birthday) 
                            VALUES (%s, %s, %s)
                            ON CONFLICT (name) DO UPDATE 
                            SET email = EXCLUDED.email, birthday = EXCLUDED.birthday
                        """, (row['name'], row['email'], row['birthday']))
                        cur.execute("CALL move_to_group(%s, %s)", (row['name'], row['group']))
                        cur.execute("CALL add_phone(%s, %s, %s)", (row['name'], row['phone'], row['phone_type']))
            conn.commit()
            print(f"Импорт из {filename} завершен.")
    except Exception as e:
        print(f"Ошибка CSV: {e}")

def main():
    limit, offset = 5, 0
    while True:
        print("\n=== PhoneBook Interface ===")
        print("1. Поиск | 2. Фильтр группы | 3. Сортировка | 4. Пагинация")
        print("5. JSON Export | 6. JSON Import | 7. CSV Import | 8. Exit")
        choice = input("Выбор: ")

        if choice == '1':
            q = input("Введите запрос: ")
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM search_contacts(%s)", (q,))
                    for r in cur.fetchall(): print(r)
        
        elif choice == '2':
            g = input("Название группы: ")
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT c.name, g.name FROM contacts c JOIN groups g ON c.group_id = g.id WHERE g.name ILIKE %s", (g,))
                    for r in cur.fetchall(): print(f"{r[0]} -> {r[1]}")

        elif choice == '3':
            col = input("Сортировать по (name/birthday): ").strip().lower()
            sort_col = col if col in ['name', 'birthday'] else 'name'
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(f"SELECT name, email, birthday FROM contacts ORDER BY {sort_col} ASC")
                    for r in cur.fetchall(): print(r)

        elif choice == '4':
            while True:
                with get_conn() as conn:
                    with conn.cursor() as cur:
                        cur.execute("SELECT name, email FROM contacts ORDER BY name LIMIT %s OFFSET %s", (limit, offset))
                        rows = cur.fetchall()
                        for r in rows: print(r)
                        nav = input("\n[next/prev/quit]: ").lower()
                        if nav == 'next' and len(rows) == limit: offset += limit
                        elif nav == 'prev': offset = max(0, offset - limit)
                        elif nav == 'quit': break
        
        elif choice == '5': 
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM search_contacts('')")
                    data = [{"name":r[1],"email":r[2],"birth":str(r[3]),"group":r[4],"phones":r[5]} for r in cur.fetchall()]
                    with open("contacts.json", "w", encoding="utf-8") as f: json.dump(data, f, indent=4, ensure_ascii=False)
            print("Экспорт в contacts.json завершен.")

        elif choice == '6': 
            import_from_json()

        elif choice == '7': 
            import_from_csv()

        elif choice == '8':
            break

if __name__ == "__main__":
    main()


def import_from_csv(filename="contacts.csv"):
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                with open(filename, mode='r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        cur.execute("SELECT id FROM contacts WHERE name = %s", (row['name'],))
                        exists = cur.fetchone()

                        if exists:
                            cur.execute("""
                                UPDATE contacts SET email = %s, birthday = %s WHERE name = %s
                            """, (row['email'], row['birthday'], row['name']))
                        else:
                            cur.execute("""
                                INSERT INTO contacts (name, email, birthday) VALUES (%s, %s, %s)
                            """, (row['name'], row['email'], row['birthday']))
                        
                        cur.execute("CALL move_to_group(%s, %s)", (row['name'], row['group']))
                        cur.execute("CALL add_phone(%s, %s, %s)", (row['name'], row['phone'], row['phone_type']))
            conn.commit()
            print(f"Импорт из {filename} завершен.")
    except Exception as e:
        print(f"Ошибка CSV: {e}")

if __name__ == "__main__":
    main()
