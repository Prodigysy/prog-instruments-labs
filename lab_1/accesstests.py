from datetime import datetime
from decimal import Decimal
from os.path import abspath

import unittest

from testutils import add_to_path, print_library_info, load_tests


CNXNSTRING = None

_TESTSTR = '0123456789-abcdefghijklmnopqrstuvwxyz-'


def _generate_test_string(length):
    """
    Generate a test string of the specified length.

    If the requested length is less than or equal to the length of `_TESTSTR`, 
    a substring of `_TESTSTR` is returned. Otherwise, `_TESTSTR` is repeated 
    as many times as necessary to meet or exceed the desired length, 
    and the result is trimmed to the exact length.

    Args:
        length (int): The desired length of the output string.

    Returns:
        str: A string of the specified length composed of repeated `_TESTSTR` content.
    """
    if length <= len(_TESTSTR):
        return _TESTSTR[:length]

    c = (length + len(_TESTSTR)-1) / len(_TESTSTR)
    v = _TESTSTR * c
    return v[:length]


class AccessTestCase(unittest.TestCase):
    """
    Test case class for testing database access using pyodbc.
    """

    SMALL_FENCEPOST_SIZES = [0, 1, 254, 255]
    LARGE_FENCEPOST_SIZES = [256, 270, 304, 508, 510, 511, 512, 1023, 1024,
                             2047, 2048, 4000, 4095, 4096,
                              4097, 10 * 1024, 20 * 1024]

    ANSI_FENCEPOSTS = [
        _generate_test_string(size) for size in SMALL_FENCEPOST_SIZES]

    UNICODE_FENCEPOSTS = [str(s) for s in ANSI_FENCEPOSTS]
    IMAGE_FENCEPOSTS = ANSI_FENCEPOSTS + [
        _generate_test_string(size) for size in LARGE_FENCEPOST_SIZES]

    def __init__(self, method_name: str) -> None:
        """
        Initializes the test case with the given method name.

        Args:
            method_name (str): The name of the test method to run.
        """
        super().__init__(method_name)

    def setUp(self) -> None:
        """
        Set up the database connection and cursor before each test.
        """
        self.cnxn: pyodbc.Connection = pyodbc.connect(CNXNSTRING)
        self.cursor: pyodbc.Cursor = self.cnxn.cursor()

        for i in range(3):
            try:
                self.cursor.execute(f"drop table t{i}")
                self.cnxn.commit()
            except:
                pass

        self.cnxn.rollback()

    def tearDown(self) -> None:
        """
        Close the cursor and connection after each test.
        """
        try:
            self.cursor.close()
            self.cnxn.close()
        except:
            pass

    def test_multiple_bindings(self) -> None:
        """
        Test multiple bindings and selects on a single cursor.
        """
        self.cursor.execute("create table t1(n int)")
        self.cursor.execute("insert into t1 values (?)", 1)
        self.cursor.execute("insert into t1 values (?)", 2)
        self.cursor.execute("insert into t1 values (?)", 3)
        for i in range(3):
            self.cursor.execute("select n from t1 where n < ?", 10)
            self.cursor.execute("select n from t1 where n < 3")

    def test_different_bindings(self) -> None:
        """
        Test binding parameters for different tables and data types.
        """
        self.cursor.execute("create table t1(n int)")
        self.cursor.execute("create table t2(d datetime)")
        self.cursor.execute("insert into t1 values (?)", 1)
        self.cursor.execute("insert into t2 values (?)", datetime.now())

    def test_datasources(self) -> None:
        """
        Test retrieving available data sources.
        """
        p: Dict[str, str] = pyodbc.dataSources()
        self.assertIsInstance(p, dict)

    def test_getinfo_string(self) -> None:
        """
        Test retrieving string information using getinfo.
        """
        value: str = self.cnxn.getinfo(pyodbc.SQL_CATALOG_NAME_SEPARATOR)
        self.assertIsInstance(value, str)

    def test_getinfo_bool(self) -> None:
        """
        Test retrieving boolean information using getinfo.
        """
        value: bool = self.cnxn.getinfo(pyodbc.SQL_ACCESSIBLE_TABLES)
        self.assertIsInstance(value, bool)

    def test_getinfo_int(self) -> None:
        """
        Test retrieving integer information using getinfo.
        """
        value: Union[
            int, int] = self.cnxn.getinfo(
                pyodbc.SQL_DEFAULT_TXN_ISOLATION)
        self.assertIsInstance(value, int)

    def test_getinfo_smallint(self) -> None:
        """
        Test retrieving small integer information using getinfo.
        """
        value: int = self.cnxn.getinfo(pyodbc.SQL_CONCAT_NULL_BEHAVIOR)
        self.assertIsInstance(value, int)

    def _test_strtype(self, sqltype: str, value: Optional[Any], resulttype: Optional[
        type] = None, colsize: Optional[int] = None) -> None:
        """
        Helper function to test string, Unicode, and binary types.

        Args:
            sqltype (str): The SQL type to use.
            value (Optional[Any]): The value to test.
            resulttype (Optional[type]): The expected result type.
            colsize (Optional[int]): The column size.
        """
        assert colsize is None or (value is None or colsize >= len(
            value)), f'colsize={colsize} value={(
                value is None) and "none" or len(value)}'

        if colsize:
            sql = f"create table t1(n1 int not null, s1 {sqltype}({colsize}), s2 {sqltype}({colsize}))"
        else:
            sql = f"create table t1(n1 int not null, s1 {sqltype}, s2 {sqltype})"

        if resulttype is None:
            if isinstance(value, str):
                resulttype = str
            else:
                resulttype = type(value)

        self.cursor.execute(sql)
        self.cursor.execute("insert into t1 values(1, ?, ?)", (value, value))
        v = self.cursor.execute("select s1, s2 from t1").fetchone()[0]

        if type(value) is not resulttype:
            value = resulttype(value)

        self.assertEqual(type(v), resulttype)

        if value is not None:
            self.assertEqual(len(v), len(value))

        self.assertEqual(v, value)


def test_unicode_null(self) -> None:
    """
    Test handling of NULL values for Unicode varchar columns.
    """
    self._test_strtype('varchar', None, colsize=255)


def _maketest(value: str) -> callable:
    """
    Factory function for creating Unicode varchar test methods.

    Args:
        value (str): The test string to insert into the varchar column.

    Returns:
        callable: A test method for the specified value.
    """
    def t(self) -> None:
        """
        Test handling of varchar column with the given Unicode string.
        """
        self._test_strtype('varchar', value, colsize=len(value))
    t.__doc__ = f"Unicode varchar with length {len(value)}"
    return t


for value in UNICODE_FENCEPOSTS:
    locals()[f'test_unicode_{len(value)}'] = _maketest(value)


def _maketest(value: str) -> callable:
    """
    Factory function for creating ANSI varchar test methods.

    Args:
        value (str): The test string to insert into the ANSI varchar column.

    Returns:
        callable: A test method for the specified value.
    """
    def t(self) -> None:
        """
        Test handling of varchar column with the given ANSI string.
        """
        self._test_strtype('varchar', value, colsize=len(value))
    t.__doc__ = f"ANSI varchar with length {len(value)}"
    return t


for value in ANSI_FENCEPOSTS:
    locals()[f'test_ansivarchar_{len(value)}'] = _maketest(value)


def _maketest(value: bytes) -> callable:
    """
    Factory function for creating binary varbinary test methods.

    Args:
        value (bytes): The test binary data to insert into the varbinary column.

    Returns:
        callable: A test method for the specified binary data.
    """
    def t(self) -> None:
        """
        Test handling of varbinary column with the given binary data.
        """
        self._test_strtype('varbinary', buffer(value), colsize=len(value), resulttype=pyodbc.BINARY)
    t.__doc__ = f"Binary varbinary with length {len(value)}"
    return t


for value in ANSI_FENCEPOSTS:
    locals()[f'test_binary_{len(value)}'] = _maketest(value)


def test_null_image(self) -> None:
    """
    Test handling of NULL values for image columns.
    """
    self._test_strtype('image', None)


def _maketest(value: bytes) -> callable:
    """
    Factory function for creating image column test methods.

    Args:
        value (bytes): The test binary data to insert into the image column.

    Returns:
        callable: A test method for the specified binary data.
    """
    def t(self) -> None:
        """
        Test handling of image column with the given binary data.
        """
        self._test_strtype('image', buffer(value), resulttype=pyodbc.BINARY)
    t.__doc__ = f"Image column with binary data length {len(value)}"
    return t


for value in IMAGE_FENCEPOSTS:
    locals()[f'test_image_{len(value)}'] = _maketest(value)


def test_null_memo(self) -> None:
    """
    Test handling of NULL values for memo columns.
    """
    self._test_strtype('memo', None)


def _maketest(value: str) -> callable:
    """
    Factory function for creating memo column test methods with Unicode input.

    Args:
        value (str): The test string to insert into the memo column.

    Returns:
        callable: A test method for the specified Unicode string.
    """
    def t(self) -> None:
        """
        Test handling of memo column with the given Unicode string.
        """
        self._test_strtype('memo', unicode(value))
    t.__doc__ = f"Unicode memo with length {len(value)}"
    return t


for value in IMAGE_FENCEPOSTS:
    locals()[f'test_memo_{len(value)}'] = _maketest(value)


def _maketest(value: str) -> callable:
    """
    Factory function for creating memo column test methods with ANSI input.

    Args:
        value (str): The test string to insert into the memo column.

    Returns:
        callable: A test method for the specified ANSI string.
    """
    def t(self) -> None:
        """
        Test handling of memo column with the given ANSI string.
        """
        self._test_strtype('memo', value)
    t.__doc__ = f"ANSI memo with length {len(value)}"
    return t
    
for value in IMAGE_FENCEPOSTS:
    locals()[f'test_ansimemo_{len(value)}'] = _maketest(value)

    def test_subquery_params(self):
        """Ensure parameter markers work in a subquery"""
        self.cursor.execute("create table t1(id integer, s varchar(20))")
        self.cursor.execute("insert into t1 values (?,?)", 1, 'test')
        row = self.cursor.execute("""
                                  select x.id
                                  from (
                                    select id
                                    from t1
                                    where s = ?
                                      and id between ? and ?
                                   ) x
                                   """, 'test', 1, 10).fetchone()
        self.assertNotEqual(row, None)
        self.assertEqual(row[0], 1)

    def _exec(self):
        self.cursor.execute(self.sql)
        
    def test_close_cnxn(self):
        """Make sure using a Cursor after closing its 
        connection doesn't crash."""

        self.cursor.execute("create table t1(id integer, s varchar(20))")
        self.cursor.execute("insert into t1 values (?,?)", 1, 'test')
        self.cursor.execute("select * from t1")
        self.cnxn.close()
        self.sql = "select * from t1"
        self.assertRaises(pyodbc.ProgrammingError, self._exec)

    def test_unicode_query(self) -> None:
        """
        Test executing a query with a Unicode string.
        """
        self.cursor.execute(u"select 1")


def test_negative_row_index(self) -> None:
    """
    Test accessing rows using negative indexing.
    """
    self.cursor.execute("create table t1(s varchar(20))")
    self.cursor.execute("insert into t1 values(?)", "1")
    row = self.cursor.execute("select * from t1").fetchone()
    self.assertEquals(row[0], "1")
    self.assertEquals(row[-1], "1")


def test_version(self) -> None:
    """
    Test that the pyodbc version is in the correct format (X.Y.Z).
    """
    self.assertEquals(3, len(pyodbc.version.split('.')))  # Example: 1.3.1


def test_datetime(self) -> None:
    """
    Test inserting and retrieving a datetime value.
    """
    value = datetime(2007, 1, 15, 3, 4, 5)
    self.cursor.execute("create table t1(dt datetime)")
    self.cursor.execute("insert into t1 values (?)", value)
    result = self.cursor.execute("select dt from t1").fetchone()[0]
    self.assertEquals(value, result)


def test_int(self) -> None:
    """
    Test inserting and retrieving an integer value.
    """
    value = 1234
    self.cursor.execute("create table t1(n int)")
    self.cursor.execute("insert into t1 values (?)", value)
    result = self.cursor.execute("select n from t1").fetchone()[0]
    self.assertEquals(result, value)


def test_negative_int(self) -> None:
    """
    Test inserting and retrieving a negative integer value.
    """
    value = -1
    self.cursor.execute("create table t1(n int)")
    self.cursor.execute("insert into t1 values (?)", value)
    result = self.cursor.execute("select n from t1").fetchone()[0]
    self.assertEquals(result, value)


def test_smallint(self) -> None:
    """
    Test inserting and retrieving a smallint value.
    """
    value = 32767
    self.cursor.execute("create table t1(n smallint)")
    self.cursor.execute("insert into t1 values (?)", value)
    result = self.cursor.execute("select n from t1").fetchone()[0]
    self.assertEquals(result, value)


def test_real(self) -> None:
    """
    Test inserting and retrieving a real (float) value.
    """
    value = 1234.5
    self.cursor.execute("create table t1(n real)")
    self.cursor.execute("insert into t1 values (?)", value)
    result = self.cursor.execute("select n from t1").fetchone()[0]
    self.assertEquals(result, value)


def test_negative_real(self) -> None:
    """
    Test inserting and retrieving a negative real (float) value.
    """
    value = -200.5
    self.cursor.execute("create table t1(n real)")
    self.cursor.execute("insert into t1 values (?)", value)
    result = self.cursor.execute("select n from t1").fetchone()[0]
    self.assertEqual(value, result)


def test_float(self) -> None:
    """
    Test inserting and retrieving a float value.
    """
    value = 1234.567
    self.cursor.execute("create table t1(n float)")
    self.cursor.execute("insert into t1 values (?)", value)
    result = self.cursor.execute("select n from t1").fetchone()[0]
    self.assertEquals(result, value)


def test_negative_float(self) -> None:
    """
    Test inserting and retrieving a negative float value.
    """
    value = -200.5
    self.cursor.execute("create table t1(n float)")
    self.cursor.execute("insert into t1 values (?)", value)
    result = self.cursor.execute("select n from t1").fetchone()[0]
    self.assertEqual(value, result)


def test_tinyint(self) -> None:
    """
    Test inserting and retrieving a tinyint value.
    """
    self.cursor.execute("create table t1(n tinyint)")
    value = 10
    self.cursor.execute("insert into t1 values (?)", value)
    result = self.cursor.execute("select n from t1").fetchone()[0]
    self.assertEqual(type(result), type(value))
    self.assertEqual(value, result)


def test_decimal(self) -> None:
    """
    Test inserting and retrieving a decimal value.
    """
    value = Decimal('12345.6789')
    self.cursor.execute("create table t1(n numeric(10,4))")
    self.cursor.execute("insert into t1 values(?)", value)
    v = self.cursor.execute("select n from t1").fetchone()[0]
    self.assertEqual(type(v), Decimal)
    self.assertEqual(v, value)


def test_money(self) -> None:
    """
    Test inserting and retrieving a money value.
    """
    self.cursor.execute("create table t1(n money)")
    value = Decimal('1234.45')
    self.cursor.execute("insert into t1 values (?)", value)
    result = self.cursor.execute("select n from t1").fetchone()[0]
    self.assertEqual(type(result), type(value))
    self.assertEqual(value, result)


def test_negative_decimal_scale(self) -> None:
    """
    Test inserting and retrieving a decimal value with negative scale.
    """
    value = Decimal('-10.0010')
    self.cursor.execute("create table t1(d numeric(19,4))")
    self.cursor.execute("insert into t1 values(?)", value)
    v = self.cursor.execute("select * from t1").fetchone()[0]
    self.assertEqual(type(v), Decimal)
    self.assertEqual(v, value)


def test_bit(self) -> None:
    """
    Test inserting and retrieving a bit (boolean) value.
    """
    self.cursor.execute("create table t1(b bit)")

    value = True
    self.cursor.execute("insert into t1 values (?)", value)
    result = self.cursor.execute("select b from t1").fetchone()[0]
    self.assertEqual(type(result), bool)
    self.assertEqual(value, result)


def test_bit_null(self) -> None:
    """
    Test inserting and retrieving a NULL bit (boolean) value.
    """
    self.cursor.execute("create table t1(b bit)")

    value = None
    self.cursor.execute("insert into t1 values (?)", value)
    result = self.cursor.execute("select b from t1").fetchone()[0]
    self.assertEqual(type(result), bool)
    self.assertEqual(False, result)


def test_guid(self):
            """
    Generates a string of the specified length using `_TESTSTR`.

    Args:
        length (int): The desired length of the string.

    Returns:
        str: A generated string of the given length.

    Description:
        This function is used to create test data. The generated string
        helps identify overlap-related issues and simplifies finding 
        breakpoints during testing.
    """
            value = "de2ac9c6-8676-4b0b-b8a6-217a8580cbee"
            self.cursor.execute("create table t1(g1 uniqueidentifier)")
            self.cursor.execute("insert into t1 values (?)", value)
            v = self.cursor.execute("select * from t1").fetchone()[0]
            self.assertEqual(type(v), type(value))
            self.assertEqual(len(v), len(value))

def test_rowcount_delete(self):
        self.assertEquals(self.cursor.rowcount, -1)
        self.cursor.execute("create table t1(i int)")
        count = 4
        for i in range(count):
            self.cursor.execute("insert into t1 values (?)", i)
        self.cursor.execute("delete from t1")
        self.assertEquals(self.cursor.rowcount, count)

def test_rowcount_nodata(self):
        """
        This represents a different code path than a delete that deleted 
        something.

        The return value is SQL_NO_DATA and code after it was causing an error.  
        We could use SQL_NO_DATA to step over
        the code that errors out and drop down to the same SQLRowCount code.  
        On the other hand, we could hardcode a
        zero return value.
        """
        self.cursor.execute("create table t1(i int)")
        self.cursor.execute("delete from t1")
        self.assertEquals(self.cursor.rowcount, 0)

def test_rowcount_select(self):
        """
        Ensure Cursor.rowcount is set properly after a select statement.

        pyodbc calls SQLRowCount after each execute and sets Cursor.rowcount, 
        but SQL Server 2005 returns -1 after a
        select statement, so we'll test for that behavior.  This is valid 
        behavior according to the DB API
        specification, but people don't seem to like it.
        """
        self.cursor.execute("create table t1(i int)")
        count = 4
        for i in range(count):
            self.cursor.execute("insert into t1 values (?)", i)
        self.cursor.execute("select * from t1")
        self.assertEquals(self.cursor.rowcount, -1)

        rows = self.cursor.fetchall()
        self.assertEquals(len(rows), count)
        self.assertEquals(self.cursor.rowcount, -1)

def test_rowcount_reset(self):
        "Ensure rowcount is reset to -1"

        self.cursor.execute("create table t1(i int)")
        count = 4
        for i in range(count):
            self.cursor.execute("insert into t1 values (?)", i)
        self.assertEquals(self.cursor.rowcount, 1)

        self.cursor.execute("create table t2(i int)")
        self.assertEquals(self.cursor.rowcount, -1)

def test_lower_case(self) -> None:
        """
        Ensure that pyodbc.lowercase forces returned column names to lowercase.
        """
        pyodbc.lowercase = True
        self.cursor = self.cnxn.cursor()

        self.cursor.execute("create table t1(Abc int, dEf int)")
        self.cursor.execute("select * from t1")

        names = [t[0] for t in self.cursor.description]
        names.sort()

        self.assertEquals(names, ["abc", "def"])

        pyodbc.lowercase = False

def test_row_description(self) -> None:
        """
        Ensure that Cursor.description is accessible as Row.cursor_description.
        """
        self.cursor = self.cnxn.cursor()
        self.cursor.execute("create table t1(a int, b char(3))")
        self.cnxn.commit()
        self.cursor.execute("insert into t1 values(1, 'abc')")

        row = self.cursor.execute("select * from t1").fetchone()
        self.assertEquals(self.cursor.description, row.cursor_description)

def test_executemany(self) -> None:
        """
        Test the executemany method to ensure multiple rows are inserted correctly.
        """
        self.cursor.execute("create table t1(a int, b varchar(10))")

        params = [(i, str(i)) for i in range(1, 6)]

        self.cursor.executemany("insert into t1(a, b) values (?,?)", params)

        count = self.cursor.execute("select count(*) from t1").fetchone()[0]
        self.assertEqual(count, len(params))

        self.cursor.execute("select a, b from t1 order by a")
        rows = self.cursor.fetchall()
        self.assertEqual(count, len(rows))

        for param, row in zip(params, rows):
            self.assertEqual(param[0], row[0])
            self.assertEqual(param[1], row[1])

def test_executemany_failure(self) -> None:
        """
        Ensure that an exception is raised if one query in an executemany call fails.
        """
        self.cursor.execute("create table t1(a int, b varchar(10))")

        params = [
            (1, 'good'),
            ('error', 'not an int'),
            (3, 'good')
        ]

        self.failUnlessRaises(pyodbc.Error, self.cursor.executemany,
                            "insert into t1(a, b) value (?, ?)", params)

def test_row_slicing(self) -> None:
        """
        Test slicing operations on row objects.
        """
        self.cursor.execute("create table t1(a int, b int, c int, d int)")
        self.cursor.execute("insert into t1 values(1,2,3,4)")

        row = self.cursor.execute("select * from t1").fetchone()

        result = row[:]
        self.failUnless(result is row)

        result = row[:-1]
        self.assertEqual(result, (1, 2, 3))

        result = row[0:4]
        self.failUnless(result is row)

def test_row_repr(self) -> None:
        """
        Test the string representation of row objects.
        """
        self.cursor.execute("create table t1(a int, b int, c int, d int)")
        self.cursor.execute("insert into t1 values(1,2,3,4)")

        row = self.cursor.execute("select * from t1").fetchone()

        result = str(row)
        self.assertEqual(result, "(1, 2, 3, 4)")

        result = str(row[:-1])
        self.assertEqual(result, "(1, 2, 3)")

        result = str(row[:1])
        self.assertEqual(result, "(1,)")

def test_concatenation(self) -> None:
        """
        Test concatenation of string columns with a literal value.
        """
        v2 = u'0123456789' * 25
        v3 = u'9876543210' * 25
        value = v2 + 'x' + v3

        self.cursor.execute("create table t1(c2 varchar(250), c3 varchar(250))")
        self.cursor.execute("insert into t1(c2, c3) values (?,?)", v2, v3)

        row = self.cursor.execute("select c2 + 'x' + c3 from t1").fetchone()

        self.assertEqual(row[0], value)

def test_autocommit(self) -> None:
        """
        Test the autocommit property of connections.
        """
        self.assertEqual(self.cnxn.autocommit, False)

        othercnxn = pyodbc.connect(CNXNSTRING, autocommit=True)
        self.assertEqual(othercnxn.autocommit, True)

        othercnxn.autocommit = False
        self.assertEqual(othercnxn.autocommit, False)

def main() -> None:
        """
        Main entry point for running tests.
        """
        from optparse import OptionParser
        parser = OptionParser(usage=usage)
        parser.add_option("-v", "--verbose", action="count",
                        help="Increment test verbosity")
        parser.add_option("-d", "--debug", action="store_true", default=False,
                        help="Print debugging items")
        parser.add_option("-t", "--test", help="Run only the named test")

        (options, args) = parser.parse_args()

        if len(args) != 1:
            parser.error('dbfile argument required')

        if args[0].endswith('.accdb'):
            driver = 'Microsoft Access Driver (*.mdb, *.accdb)'
        else:
            driver = 'Microsoft Access Driver (*.mdb)'

        global CNXNSTRING
        CNXNSTRING = (
            'DRIVER={%s};DBQ=%s;ExtendedAnsiSQL=1' % (driver, abspath(args[0])))

        cnxn = pyodbc.connect(CNXNSTRING)
        print_library_info(cnxn)
        cnxn.close()

        suite = load_tests(AccessTestCase, options.test)

        testRunner = unittest.TextTestRunner(verbosity=options.verbose)
        result = testRunner.run(suite)

    if __name__ == '__main__':
        add_to_path()
        import pyodbc
        main()
