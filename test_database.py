# test_database.py

import unittest
import database


class TestDatabase(unittest.TestCase):

    def test_database_connection(self):
        """
        Test database connectivity.
        """
        cnxn = database.get_sql_connection()
        self.assertIsNotNone(cnxn, "Database connection failed.")
        cnxn.close()

    def test_fetch_data_from_sql(self):
        """
        Test data fetching from the database.
        """
        query = "SELECT TOP 10 customer_account_id FROM InvoiceData"
        df = database.fetch_data_from_sql(query)
        self.assertIsNotNone(df, "Fetching data failed.")


if __name__ == '__main__':
    unittest.main()
