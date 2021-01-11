# TechConf Registration Website

## Project Overview
The TechConf website allows attendees to register for an upcoming conference. Administrators can also view the list of attendees and notify all attendees via a personalized email message.

The application is currently working but the following pain points have triggered the need for migration to Azure:
 - The web application is not scalable to handle user load at peak
 - When the admin sends out notifications, it's currently taking a long time because it's looping through all attendees, resulting in some HTTP timeout exceptions
 - The current architecture is not cost-effective 

In this project, you are tasked to do the following:
- Migrate and deploy the pre-existing web app to an Azure App Service
- Migrate a PostgreSQL database backup to an Azure Postgres database instance
- Refactor the notification logic to an Azure Function via a service bus queue message

## Dependencies

You will need to install the following locally:
- [Postgres](https://www.postgresql.org/download/)
- [Visual Studio Code](https://code.visualstudio.com/download)
- [Azure Function tools V3](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=windows%2Ccsharp%2Cbash#install-the-azure-functions-core-tools)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)
- [Azure Tools for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=ms-vscode.vscode-node-azure-pack)

## Project Instructions

### Part 1: Create Azure Resources and Deploy Web App
1. Create a Resource group
2. Create an Azure Postgres Database single server
   - Add a new database `techconfdb`
   - Allow all IPs to connect to database server
   - Restore the database with the backup located in the data folder
3. Create a Service Bus resource with a `notificationqueue` that will be used to communicate between the web and the function
   - Open the web folder and update the following in the `config.py` file
      - `POSTGRES_URL`
      - `POSTGRES_USER`
      - `POSTGRES_PW`
      - `POSTGRES_DB`
      - `SERVICE_BUS_CONNECTION_STRING`
4. Create App Service plan
5. Create a storage account
6. Deploy the web app

### Part 2: Create and Publish Azure Function
1. Create an Azure Function in the `function` folder that is triggered by the service bus queue created in Part 1.

      **Note**: Skeleton code has been provided in the **README** file located in the `function` folder. You will need to copy/paste this code into the `__init.py__` file in the `function` folder.
      - The Azure Function should do the following:
         - Process the message which is the `notification_id`
         - Query the database using `psycopg2` library for the given notification to retrieve the subject and message
         - Query the database to retrieve a list of attendees (**email** and **first name**)
         - Loop through each attendee and send a personalized subject message
         - After the notification, update the notification status with the total number of attendees notified
2. Publish the Azure Function

### Part 3: Refactor `routes.py`
1. Refactor the post logic in `web/app/routes.py -> notification()` using servicebus `queue_client`:
   - The notification method on POST should save the notification object and queue the notification id for the function to pick it up
2. Re-deploy the web app to publish changes

## Monthly Cost Analysis
Complete a month cost analysis of each Azure resource to give an estimate total cost using the table below:

| Azure Resource | Service Tier | Monthly Cost |
| ------------ | ------------ | ------------ |
| *Azure Postgres Database* | Basic   |       $25.8       |
| *Azure Service Bus*   |   Basic    |   $0.05           |
| *Azure Web App Service* |   F1      |    Free          |
| *Azure Function App Service* |  Consumption   | Free             |
| *Azure Storage Account * |  General Purpose v2        |   $0.5          |

## Architecture Explanation
This is a placeholder section where you can provide an explanation and reasoning for your architecture selection for both the Azure Web App and Azure Function.

For Azure Web App and Azure Function, I am selecting the **F1** and **consumption** free services. This migration exercise  is a Nanodegree project. We do not expect any large transactions, but the full features are expected. The Web App and Azure Function provides me with some nice features:

- Support Linux and Python development
- Built-in load balancing and autoscale (this will be useful if the project goes real)
- Fully integration with Visaul Studio Code for easy deployment and debugging
- Provide Azure security 
- High availability

 


##

### The code for **notification** function in the **Function App**  updated

'''
@app.route('/Notification', methods=['POST', 'GET'])
def notification():
    if request.method == 'POST':
        mynotification = Notification()
        mynotification.message = request.form['message']
        mynotification.subject = request.form['subject']
        mynotification.status = 'Notifications submitted'
        mynotification.submitted_date = datetime.utcnow()

        try:
            db.session.add(mynotification)
            db.session.commit()

            # #################################################
            # TODO: Refactor This logic into an Azure Function
            # Code below will be replaced by a message queue
            #################################################
            '''
            attendees = Attendee.query.all()

            for attendee in attendees:
                subject = '{}: {}'.format(attendee.first_name, notification.subject)
                send_email(attendee.email, subject, notification.message)

            notification.completed_date = datetime.utcnow()
            notification.status = 'Notified {} attendees'.format(len(attendees))
            db.session.commit()
            
            '''

            # TODO Call servicebus queue_client to enqueue notification ID

            #fetches the Id of the record saved in tableT, Andrew 01/10/2021
            notification_Id = mynotification.id
            msg = Message(str(notification_Id))
            
            # sends message to queue
            queue_client.send(msg)
            #################################################
            # END of TODO
            #################################################

            return redirect('/Notifications')
        except :
            logging.error('log unable to save notification')

    else:
        return render_template('notification.html')
'''


### The code for **Web App** updated for __init__.py:

'''
def main(msg: func.ServiceBusMessage):

    try:
        notification_id = int(msg.get_body().decode('utf-8'))
        logging.info("Python ServiceBus queue trigger processed message: %s",notification_id)
    except Exception as err:
        logging.error("Error in Getting ServiceBus Message")
        logging.error(err)

    # TODO: Get connection to database
    try:
        dbconn=psycopg2.connect(dbname='techconfdb', user='azureuser@techconf-server',
         host='techconf-server.postgres.database.azure.com', password='P@ssword')
        cursor = dbconn.cursor()
    except Exception as err:
        logging.error(err)
    try:
        # TODO: Get notification message and subject from database using the notification_id
        cursor.execute("Select message, subject from notification where id= {} ;".format(notification_id))
        notificationQuery = cursor.fetchone()
        # TODO: Get attendees email and name
        #conf_attendees = cursor.execute("Select first_name, last_name, email from attendee;")
        cursor.execute("Select first_name, last_name, email from attendee;")
        conf_attendees = cursor.fetchall()
        # TODO: Loop through each attendee and send an email with a personalized subject

        for attendee in conf_attendees:
            Mail("{},{},{}".format({'azureuser@techconf-server'},{attendee[2]},{notificationQuery}))
        notification_sent_date = datetime.utcnow()
        notification_status = 'Notified {} conference attendees'.format(len(conf_attendees))

        # TODO: Update the notification table by setting the completed date and updating the status with the total number of attendees notified
        
        #notification_id = 59
        updateQuery_str = "Update notification SET status =  '{}', completed_date = '{}' where id={:d}; ".format(
            notification_status,notification_sent_date,notification_id)
        logging.info(updateQuery_str)
        cursor.execute(updateQuery_str)
        dbconn.commit()
        logging.info("Notification has been updated")
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        # TODO: Close connection
        dbconn.close()
'''