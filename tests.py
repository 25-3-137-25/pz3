from manager import DatabaseManager


# creating smth in the table

with DatabaseManager() as db: db.create('do_not_touch_please_by_ivan', {'name': 'Иван', 'age': 25, 'email': 'ivanko7002@gmail.com'})


# reading with some conditions

with DatabaseManager() as db: print(db.read('do_not_touch_please_by_ivan', conditions={'age': 25}))


#updating info

with DatabaseManager() as db: db.update('do_not_touch_please_by_ivan', {'age': 26}, {'name': 'Иван'})


#deleting some info with conditions

with DatabaseManager() as db: db.delete('do_not_touch_please_by_ivan', {'name': 'Иван'})


# execute query

with DatabaseManager() as db: print(db.execute_query("SELECT * FROM do_not_touch_please_by_ivan"))


#checking for the existance of our table

with DatabaseManager() as db: print(db.table_exists('do_not_touch_please_by_ivan'))