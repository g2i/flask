from src.services.xero.xero_data_sync import XeroDataSync

def main():
    syncer = XeroDataSync()
    syncer.sync_data()

if __name__ == "__main__":
    main()