import logging
import azure.functions as func
import psycopg2
import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def main(msg: func.ServiceBusMessage):

    try:
        notification_id =msg.get_body().decode('utf-8')
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
        #notificationQuery = cursor.execute("Select message, subject from notification where id= {} ;".format(notification_id))
        cursor.execute("Select message, subject from notification where id = 22 ;")
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
        
        notification_updateQuery = cursor.execute("Update notification SET status =  '{}', completed_date = '{}' where id = {}; ".format(
            notification_status,notification_sent_date,22))
        dbconn.commit()
        logging.info("Notification has been updated")
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        # TODO: Close connection
        dbconn.close()
