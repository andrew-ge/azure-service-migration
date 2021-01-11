## Screenshots

The following screenshots should be taken and uploaded to this **screenshots** folder:

1. **Migrate Web Applications - 2 Screenshots**
 - Screenshot of Azure Resource showing the **App Service Plan**.
 - Screenshot of the deployed Web App running. The screenshot should be fullscreen showing the URL and application running.
2. **Migrate Database - 2 Screenshots**
 - Screenshot of the Azure Resource showing the **Azure Database for PostgreSQL server**.
 - Screenshot of the Web App successfully loading the list of **attendees** and **notifications** from the deployed website.
3. **Migrate Background Process - 4 Screenshots**
 - Screenshot of the Azure Function App running in Azure, showing the **function name** and the **function app plan**.
 - Screenshots of the following showing functionality of the deployed site:
    1. Submitting a new notification.
      - Screenshot of filled out **Send Notification** form.
    2. Notification processed after executing the Azure function.
      - Screenshot of the **Email Notifications List** showing the notification status as **Notifications submitted**.
      - Screenshot of the **Email Notifications List** showing the notification status as **Notified X attendees**.



## Analysis

### Monthly Cost Analysis


### Architecture Explanation



## Code updated



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