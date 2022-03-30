import sqlite3

# может cur и не нужен

class DBHelper:
    def __init__(self, dbname="user_rates.db"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)

    def setup(self):
        cur = self.conn.cursor()
        rates = '''CREATE TABLE IF NOT EXISTS rates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id int,
            user_ans text,
            correct_ans text,
            if_correct int
            )'''
        users = '''CREATE TABLE IF NOT EXISTS users (
            user_id int,
            name text
            )'''
        cur.execute(rates)
        cur.execute(users)
        self.conn.commit()

    def check(self, user_id):
        cur = self.conn.cursor()
        check = 'SELECT user_id FROM users WHERE user_id = ?'
        first = cur.execute(check, (user_id, )).fetchone()
        return first

    def add_item_users(self, user_id, name):
        cur = self.conn.cursor()
        check = 'SELECT user_id FROM users WHERE user_id = ?'
        first = cur.execute(check, (user_id, )).fetchone()
        if first == None:
            ins_users = "INSERT INTO users (user_id, name) VALUES (?, ?)"
            args = (user_id, name)
            cur.execute(ins_users, args)
            self.conn.commit()
        else:
            change_user = "UPDATE users SET name = ? WHERE user_id = ?"
            args = (name, user_id)
            cur.execute(change_user, args)
            self.conn.commit()
        return first

    def add_item_rates(self, user_id, user_ans, correct_ans, if_correct):
        cur = self.conn.cursor()
        ins_rates = 'INSERT INTO rates (user_id, user_ans, correct_ans, if_correct) VALUES (?, ?, ?, ?)'
        args = (user_id, user_ans, correct_ans, if_correct)
        cur.execute(ins_rates, args)
        self.conn.commit()

    def get_statistics(self, user_id):
        cur = self.conn.cursor()
        correct_ans_query = '''
        SELECT user_id, COUNT(if_correct)
        FROM rates
        WHERE user_id = ? AND if_correct = 1
        '''
        correct_ans = cur.execute(correct_ans_query, (user_id, )).fetchone()[1]

        all_ans_query = '''
        SELECT user_id, COUNT(if_correct)
        FROM rates
        WHERE user_id = ?
        '''
        all_ans = cur.execute(all_ans_query, (user_id, )).fetchone()[1]

        most_difficult_guess_query = '''
        SELECT user_id, if_correct, COUNT(correct_ans) as cnt, correct_ans
        FROM rates
        WHERE if_correct = 0 AND user_id = ?
        GROUP BY correct_ans
        ORDER BY cnt DESC
        '''
        mistakes, most_difficult_guess = cur.execute(most_difficult_guess_query, (user_id, )).fetchone()[2:]

        bot_answer = f'*Correct answers:* {correct_ans}\n' + \
                f'*All answers:* {all_ans}\n' + \
                f'*Ratio of correct answers:* {round(correct_ans/all_ans, 2)}\n' +\
                f'*Most difficult guess:* {most_difficult_guess}, *mistakes:* {mistakes}'
        
        return bot_answer

    def get_rating(self, user_id):
        cur = self.conn.cursor()
        rating_query = '''
        SELECT users.name, SUM(if_correct) as sum_ans, users.user_id
        FROM rates
        JOIN users ON rates.user_id = users.user_id
        GROUP BY rates.user_id
        ORDER BY sum_ans DESC
        '''
        rating = cur.execute(rating_query).fetchall()
        top_5 = rating[:5]
        for i, user in enumerate(rating):
            if user[-1] == user_id:
                place = i
        bot_answer = '\n'.join(
            [f'{i+1}. *{top_5[i][0]}* has *{top_5[i][1]}* right answers' for i in range(len(top_5))]) + \
            '\n' + '-'*10 +\
            f'\nYour place in the leaderboard: {place+1}'

        return bot_answer
