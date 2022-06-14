from flask import Flask, render_template, json, redirect
from flask_mysqldb import MySQL
from flask import request
import os


app = Flask(__name__)



app.config['MYSQL_HOST'] = 'classmysql.engr.oregonstate.edu'
app.config['MYSQL_USER'] = 'cs340_kamanda'
app.config['MYSQL_PASSWORD'] = '9279'
app.config['MYSQL_DB'] = 'cs340_kamanda'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'


mysql = MySQL(app)


# Routes 
@app.route('/')
def root():
    #Homepage route, brief description of the project/site
    return render_template("homepage.j2")


#Cars route, provides method to add/delete cars
@app.route('/cars', methods =['POST', 'GET'])
def route1():  

    #print(rv)

    #Separate out the request methods, in this case this is for a POST
    #submission to create an INSERT into the DB. A hidden form value has
    #been added to differentiate between INSERT & DELETE
    if request.method == 'POST':
        #Check if the user is submitting or deleting
        if request.form.get('Submit'):
            #Grab all the form data
            carMake = request.form['carMake']
            carModel = request.form['carModel']
            carYear = request.form['carYear']
            carColor = request.form['carColor']
            carPrice = request.form['carPrice']
            print(carMake, carModel, carYear, carColor, carPrice)

            #Write and execute the query to insert the Car and then refresh the page for new values
            query = "INSERT INTO Cars (make, model, model_year, color, price) VALUES (%s, %s,%s,%s,%s)"
            cur = mysql.connection.cursor()
            cur.execute(query, (carMake, carModel, carYear, carColor, carPrice))
            mysql.connection.commit()

            query = "SELECT * FROM Cars;"
            cur = mysql.connection.cursor()
            cur.execute(query)
            rv = cur.fetchall()

            return redirect("/cars")

        #User wants to delete a specific ID
        if request.form.get('Delete'):

            #Get car id from the user
            carID = request.form['carID']

            #Execute the delete query and refresh the page
            query = "DELETE FROM Cars WHERE car_id = %s"
            cur = mysql.connection.cursor()
            cur.execute(query, (carID,))
            mysql.connection.commit()
            print(carID)

            return redirect("/cars")

    #This method is for generating the page to display the table data
    if request.method == 'GET':
        #Query to grab the car data for display
        query = "SELECT * FROM Cars;"
        cur = mysql.connection.cursor()
        cur.execute(query)
        rv = cur.fetchall()
        
        return render_template("table_cars.j2", data=rv)


#This route allows you to view the Salesrep data to create/delete a rep
@app.route('/salesreps', methods=['POST', 'GET'])
def route2():
    if request.method == 'POST':
        #Check for a submission from the user
        if request.form.get('Submit'):
            print("Submit method")
            #Grab the form data
            repFirstName = request.form['firstName']
            repLastName = request.form['lastName']

            print(repFirstName, repLastName)

            #Generate and execute the query to insert the data and refresh the page
            query = "INSERT INTO Salesreps (rep_fname, rep_lname) VALUES (%s, %s)"
            cur = mysql.connection.cursor()
            cur.execute(query, (repFirstName, repLastName))
            mysql.connection.commit()

            return redirect("/salesreps")

        #Check for delete request 
        if request.form.get('Delete'):
            print("Delete method")
            #Grab the form data
            repID = request.form['repID']

            #Generate and execute the query to delete the data and refresh the page
            query = "DELETE FROM Salesreps WHERE rep_id = %s"
            cur = mysql.connection.cursor()
            cur.execute(query, (repID))
            mysql.connection.commit()
            print(repID)

            return redirect("/salesreps")

    #This method is for generating the page to display the table data
    if request.method == 'GET':
        query = "SELECT * FROM Salesreps;"

        cur = mysql.connection.cursor()
        cur.execute(query)
        rv = cur.fetchall()

        return render_template("table_sales.j2", data=rv)

#This route allows you to view invoices and search using specified criteria.
#Users can also update, delete, and insert new invoices.
@app.route('/invoices', methods=['POST', 'GET'])
def route3():
    
    if request.method == 'POST':
        #Check for a a search request from the user
        if request.form.get('Search'):
            print("Search button")
            customerID = request.form['customerID']
            repID = request.form['repID']
            invoicePrice = request.form['invoicePrice']
            saleDate = request.form['saleDate']
            print(customerID, repID, invoicePrice, saleDate)


            if customerID == '0':
                print("Null customer")
            if repID == '0':
                print("Null rep")
            if invoicePrice == '':
                print("Null price")
            if saleDate == '':
                print("Null date")
            
            #if all are empty return all invoices
            #For all that are not 0 or empty return the query with those conditions
            if customerID == '0' and repID == '0' and invoicePrice == '' and saleDate == '':
                return redirect("/invoices")
            else:
                #Begin building the search query string by adding the conditions one by one
                query1 = "SELECT Invoices.invoice_id, Invoices.customer_id, Invoices.rep_id, CONCAT(Customers.customer_fname,' ', Customers.customer_lname) AS customer_name, CONCAT(Salesreps.rep_fname, ' ', Salesreps.rep_lname) AS salesrep_name, Invoices.total_price, Invoices.date FROM Invoices LEFT JOIN Customers ON Invoices.customer_id = Customers.customer_id LEFT JOIN Salesreps ON Invoices.rep_id = Salesreps.rep_id WHERE "

                valueArray = []

                if customerID != '0':
                    query1 += "Invoices.customer_id= %s "
                    valueArray.append(customerID)
                if repID != '0':
                    if len(valueArray) > 0:
                        query1 += "AND Invoices.rep_id=%s "
                    else:
                        query1 += "Invoices.rep_id=%s "
                    valueArray.append(repID)
                if invoicePrice != '':
                    if len(valueArray) > 0:
                        query1 += "AND Invoices.total_price=%s "
                    else:
                        query1 += "Invoices.total_price=%s "
                    valueArray.append(invoicePrice)
                if saleDate != '':
                    if len(valueArray) > 0:
                        query1 += "AND Invoices.date=%s "
                    else:
                        query1 += "Invoices.date=%s "
                    valueArray.append(saleDate)
                
                print(query1)

                #Query to gather the dropdown data for the page for both customers and salesreps
                query2 = "SELECT Customers.customer_id AS customerID, CONCAT(Customers.customer_fname,' ', Customers.customer_lname) AS customer_name_drop FROM Customers;"

                query3 = "SELECT Salesreps.rep_id AS repID, CONCAT(Salesreps.rep_fname,' ', Salesreps.rep_lname) AS salesrep_name_drop FROM Salesreps;"

                #Execute all the queries
                cur = mysql.connection.cursor()
                cur.execute(query1,valueArray)
                query1data = cur.fetchall()

                cur = mysql.connection.cursor()
                cur.execute(query2)
                query2data = cur.fetchall()

                cur = mysql.connection.cursor()
                cur.execute(query3)
                query3data = cur.fetchall()

                #Combine all the query data into on output array to pass to the front end
                output = [query1data, query2data, query3data]

                return render_template("table_invoices.j2", data=output)

        #Check for a submission from the user
        if request.form.get('Submit'):
            print("Submit button")
            #Gath the form data
            customerID = request.form['customerID']
            repID = request.form['repID']
            invoicePrice = request.form['invoicePrice']
            saleDate = request.form['saleDate']

            print(customerID, repID, invoicePrice, saleDate)

            #Two conditions for submissions: Null rep id or non-null rep id
            #Depending on the user conditions the queries are different.
            #Page refresh after they are committed
            if repID == '0':
                query = "INSERT INTO Invoices (customer_id, rep_id, total_price, date) VALUES (%s, NULL, %s, %s)"
                cur = mysql.connection.cursor()
                cur.execute(query, (customerID, invoicePrice, saleDate))
                mysql.connection.commit()
            else:
                query = "INSERT INTO Invoices (customer_id, rep_id, total_price, date) VALUES (%s, %s, %s, %s)"
                cur = mysql.connection.cursor()
                cur.execute(query, (customerID, repID, invoicePrice, saleDate))
                mysql.connection.commit()


            return redirect("/invoices")

        #Check for a delete request from the user
        if request.form.get('Delete'):
            #Get the form data
            invoiceID = request.form['invoiceID']

            #Generate and execute the delete query, then refresh the page
            query = "DELETE FROM Invoices WHERE invoice_id = %s"
            cur = mysql.connection.cursor()
            cur.execute(query, (invoiceID))
            mysql.connection.commit()
            print(invoiceID)
            return redirect("/invoices")

    if request.method == 'GET':
        #Generate 3 queries to populate the table and the two dropdowns for customer and salesrep data
        query1 = "SELECT Invoices.invoice_id, Invoices.customer_id, Invoices.rep_id, CONCAT(Customers.customer_fname,' ', Customers.customer_lname) AS customer_name, CONCAT(Salesreps.rep_fname, ' ', Salesreps.rep_lname) AS salesrep_name, Invoices.total_price, Invoices.date FROM Invoices LEFT JOIN Customers ON Invoices.customer_id = Customers.customer_id LEFT JOIN Salesreps ON Invoices.rep_id = Salesreps.rep_id;"

        query2 = "SELECT Customers.customer_id AS customerID, CONCAT(Customers.customer_fname,' ', Customers.customer_lname) AS customer_name_drop FROM Customers;"

        query3 = "SELECT Salesreps.rep_id AS repID, CONCAT(Salesreps.rep_fname,' ', Salesreps.rep_lname) AS salesrep_name_drop FROM Salesreps;"

        #Execute all the queries
        cur = mysql.connection.cursor()
        cur.execute(query1)
        query1data = cur.fetchall()

        cur = mysql.connection.cursor()
        cur.execute(query2)
        query2data = cur.fetchall()

        cur = mysql.connection.cursor()
        cur.execute(query3)
        query3data = cur.fetchall()

        #Combine the query data into one output array
        output = [query1data,query2data,query3data]

        return render_template("table_invoices.j2", data=output)

#This page allows users to view customers, add new customers and delete customers
@app.route('/customers', methods=['POST', 'GET'])
def route4():

    if request.method == 'POST':
        #Check for submission from user
        if request.form.get("Submit"):
            print("Submit method")
            
            #Gather the form data
            firstName = request.form['customerFirstName']
            lastName = request.form['customerLastName']
            street = request.form['street']
            zip = request.form['zip']
            state = request.form['state']
            phone = request.form['phone']

            print(firstName, lastName, street, zip, state, phone)

            #Generate the query, execute and refresh the page
            query = "INSERT INTO Customers (customer_fname, customer_lname, street, zip, state, phone_number) VALUES (%s, %s, %s, %s, %s, %s)"
            cur = mysql.connection.cursor()
            cur.execute(query, (firstName, lastName, street, zip, state, phone))
            mysql.connection.commit()

            return redirect("/customers")

        #Check for a delete request
        if request.form.get('Delete'):
            print("Delete method")
            
            #Gather the form data
            customerID = request.form['customerID']

            #Generate and execute the delete query. Then refresh the page
            query = "DELETE FROM Customers WHERE customer_id = %s"
            cur = mysql.connection.cursor()
            cur.execute(query, (customerID))
            mysql.connection.commit()

            return redirect("/customers")
    
    if request.method == 'GET':
        #Simple query to fetch all the customer table data
        query = "SELECT * FROM Customers;"

        cur = mysql.connection.cursor()
        cur.execute(query)
        rv = cur.fetchall()
        return render_template("table_customers.j2", data=rv)


#This route allows users to view the links between a cars and invoices.
#Users can link new cars to invoices and delete those links.
@app.route('/carsinvoices', methods=['POST', 'GET'])
def route5():

    if request.method == 'POST':
        #Check for new submissions
        if request.form.get("Submit"):
            print("Submit method")

            #Get the form data from the user
            invoiceID = request.form['invoiceID']
            carID = request.form['carID']
            quantity = request.form['quantity']

            print(invoiceID, carID, quantity)

            #Generate and execute the insert query. Refresh the page to show the new data
            query = "INSERT INTO Cars_Invoices (car_id, invoice_id, quantity) VALUES (%s, %s, %s)"
            cur = mysql.connection.cursor()
            cur.execute(query, (carID, invoiceID,quantity))
            mysql.connection.commit()

            return redirect("/carsinvoices")
        #Check for a delete request
        if request.form.get('Delete'):
            #Gather the form data
            carinvoiceID = request.form['carinvoiceID']

            #Generate and execute the query based on the form id. Refresh the page after.
            query = "DELETE FROM Cars_Invoices WHERE car_invoice_id = %s"
            cur = mysql.connection.cursor()
            cur.execute(query, (carinvoiceID))
            mysql.connection.commit()
            print(carinvoiceID)

            return redirect("/carsinvoices")

    if request.method == 'GET':
        #Generate 3 queries; one for the table, one for the invoice dropdown, one for the car dropdown
        query = "SELECT * FROM Cars_Invoices;"
        query2 = "SELECT invoice_id FROM Invoices"
        query3 = "SELECT car_id, model FROM Cars"

        #Execute all 3 queries
        cur = mysql.connection.cursor()
        cur.execute(query)
        query1data = cur.fetchall()

        cur = mysql.connection.cursor()
        cur.execute(query2)
        query2data = cur.fetchall()

        cur = mysql.connection.cursor()
        cur.execute(query3)
        query3data = cur.fetchall()

        #Combine the data into one output array and pass it to the front end
        output = [query1data,query2data, query3data]

        print(output)
        return render_template("table_car_invoice.j2", data=output)

#This page is accessed by the update button on the invoice page.
#It takes in an invoice and displays that invoice data on the table.
#The user can the adjust all of the data on that invoice and submit it.
@app.route('/updateinvoice', methods=['POST', 'GET'])
def route6():

    #Check for the update request from the invoice page
    if request.form.get("Update"):

        #Get the id of the invoice that was passed
        invoiceID = request.form['invoiceID']

        #Gather the data on this invoice id as well as all the customer and rep id data for the dropdowns
        query1 = "SELECT Invoices.invoice_id, Invoices.customer_id, Invoices.rep_id, CONCAT(Customers.customer_fname,' ', Customers.customer_lname) AS customer_name, CONCAT(Salesreps.rep_fname, ' ', Salesreps.rep_lname) AS salesrep_name, Invoices.total_price, Invoices.date FROM Invoices LEFT JOIN Customers ON Invoices.customer_id = Customers.customer_id LEFT JOIN Salesreps ON Invoices.rep_id = Salesreps.rep_id WHERE invoice_id = %s"
        query2 = "SELECT customer_id, CONCAT(customer_fname, ' ', customer_lname) AS customer_name FROM Customers"
        query3 = "SELECT rep_id, CONCAT(rep_fname, ' ', rep_lname) AS rep_name FROM Salesreps"

        #Execute all the queries
        cur = mysql.connection.cursor()
        cur.execute(query1,[invoiceID])
        query1data = cur.fetchall()

        cur = mysql.connection.cursor()
        cur.execute(query2)
        query2data = cur.fetchall()

        cur = mysql.connection.cursor()
        cur.execute(query3)
        query3data = cur.fetchall()

        #Combine the output data into one array and pass it to the frontend
        output = [query1data, query2data, query3data]

        return render_template("update_invoice.j2", data=output)
    #Check for a submission from the user, confirming that they want to update the invoice
    if request.form.get("Submit"):

        #Gather the new invoice data
        invoiceID = request.form['invoiceID']
        customerID = request.form['customerID']
        repID = request.form['repID']
        invoicePrice = request.form['invoicePrice']
        saleDate = request.form['saleDate']

        cur = mysql.connection.cursor()

        #There are two options again if the user the user wants to set the rep id to NULL
        #Therefore a special query was generated for that option.
        #Afterwards execute the update queries
        if repID == "0":
            query = "UPDATE Invoices SET Invoices.customer_id = %s, Invoices.rep_id = NULL, Invoices.total_price = %s, Invoices.date = %s WHERE Invoices.invoice_id = %s"
            cur.execute(query, (customerID,
                        invoicePrice, saleDate, invoiceID))
            mysql.connection.commit()
        else:
            query = "UPDATE Invoices SET Invoices.customer_id = %s, Invoices.rep_id = %s, Invoices.total_price = %s, Invoices.date = %s WHERE Invoices.invoice_id = %s"
            cur.execute(query, (customerID, repID, invoicePrice, saleDate, invoiceID))
            mysql.connection.commit()

        #Refresh the page
        print("updated")
        return redirect("/invoices")

    


# Listener
if __name__ == "__main__":
    #Start the app on port 3000, it will be different once hosted
    app.run(port=3000, debug=True)
