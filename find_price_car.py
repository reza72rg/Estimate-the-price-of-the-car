import requests
import mysql.connector
from bs4 import BeautifulSoup
from sklearn import tree

# Constants
URL = 'https://www.hamrah-mechanic.com/cars-for-sale/irankhodro/peugeot206/'

# Database connection
mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='***********',
    database='cars'
)

# Data extraction function
def extract_data(car):
    # Extract title
    title = car.find('span', {'class': 'carCard_header__name__ib5RB'}).text.strip()
    model, year = title.split('مدل')
    model = model.strip()[4:]
    model = int(model)
    year = year.strip()
    year = int(year)

    # Extract price
    price = car.find('div', {'class': 'carCard_price-container__cost__BO_Hy'}).text.strip()
    price = price.split('تومان')[0].replace(',', '').strip()
    price = int(price)

    # Extract location
    location = car.find('span', {'class': 'mr-1'}).text.strip()
    if location == 'تهران':
        location = 'tehran'
    elif location == 'کرج':
        location = 'karaj'

    # Extract kilometers
    kilometr = car.find('span', {'dir': 'ltr'}).text.strip()
    kilometr = kilometr.split('KM')[0].replace(',', '').strip()
    try:
        kilometr = int(kilometr)
    except:
        pass
    if kilometr == 'صفر':
        kilometr = 0

    return (model, year, kilometr, price, location)


# Main function
response = requests.get(URL)
soup = BeautifulSoup(response.content, 'html.parser')
cars = soup.find_all('div', {'class': 'list_list-item__XdvG4 gtm-cfs-16'})
data = [extract_data(car) for car in cars]

table = mydb.cursor()

# Create table if not exists
table.execute("CREATE TABLE IF NOT EXISTS My_cars(Customer_id INT PRIMARY KEY AUTO_INCREMENT,Model INT,Year INT, Kilometr INT ,Price INT,Location varchar(25))")

# Insert new data into the table
key = "INSERT INTO My_cars (model, year, kilometr,price,location) VALUES (%s, %s, %s, %s, %s)"
table2 = mydb.cursor()
table2.execute("SELECT * FROM My_cars")
my_list = list()
for q in table2:
    my_list.append(q[1:])
for i in data:
    if i not in my_list:
        table.execute(key, i)
        mydb.commit()

x = list()
y = list()
table2 = mydb.cursor()
table2.execute("SELECT * FROM My_cars")
for q in table2:
    x.append(q[2:4])
    y.append(q[4])

# Train the decision tree classifier
clf = tree.DecisionTreeClassifier()
clf = clf.fit(x, y)

# Get input from the user
year1 = int(input("Enter the year of your car: "))
kilometr1 = int(input("Enter the kilometers of your car: "))

# Predict the price using the trained model
new_data = [[year1, kilometr1]]
answer = clf.predict(new_data)

# Print the predicted price
for c in answer:
    print(format(c, ","))
