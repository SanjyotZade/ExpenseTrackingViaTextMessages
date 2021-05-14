from EmailDataProcurement import EmailDataProcurement

if __name__ == "__main__":
    process_obj = EmailDataProcurement()
    process_obj.start_the_push_service()
    print(process_obj.start_pubsub_communication())
