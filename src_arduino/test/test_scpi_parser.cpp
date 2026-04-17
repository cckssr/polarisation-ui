#include <unity.h>
#include <string>
#include <cctype>

// Mock für PlatformIO native testingpi
#ifdef UNIT_TEST

// Minimal Arduino String mock für Testing
class StringMock
{
public:
    std::string value;

    StringMock() {}
    StringMock(const char *c) : value(c) {}
    StringMock(const std::string &s) : value(s) {}

    int indexOf(char c, int from = 0) const
    {
        size_t pos = value.find(c, from);
        return (pos == std::string::npos) ? -1 : pos;
    }

    int indexOf(const char *str, int from = 0) const
    {
        size_t pos = value.find(str, from);
        return (pos == std::string::npos) ? -1 : pos;
    }

    StringMock substring(int start, int end = -1) const
    {
        if (end == -1)
            end = value.length();
        return StringMock(value.substr(start, end - start));
    }

    void trim()
    {
        size_t start = value.find_first_not_of(" \t\r\n");
        size_t end = value.find_last_not_of(" \t\r\n");
        if (start != std::string::npos)
        {
            value = value.substr(start, end - start + 1);
        }
        else
        {
            value = "";
        }
    }

    void toUpperCase()
    {
        for (char &c : value)
        {
            c = toupper(c);
        }
    }

    bool endsWith(const char *suffix) const
    {
        size_t len = strlen(suffix);
        return (value.length() >= len &&
                value.substr(value.length() - len) == suffix);
    }

    int length() const { return value.length(); }

    const char *c_str() const { return value.c_str(); }

    operator std::string() const { return value; }
};

// Define String as StringMock for tests
#define String StringMock

// SCPI Parser from actual code (copied for testing)
bool scpiParse(const String &line, String &header, String &param, bool &isQuery)
{
    if (line.length() == 0)
        return false;

    int sp = line.indexOf(' ');
    if (sp >= 0)
    {
        header = line.substring(0, sp);
        param = line.substring(sp + 1);
        param.trim();
    }
    else
    {
        header = line;
        param = "";
    }

    isQuery = header.endsWith("?");
    if (isQuery)
        header = header.substring(0, header.length() - 1);

    header.toUpperCase();
    param.toUpperCase();
    return true;
}

// ─── Tests ────────────────────────────────────────────────────────────────

void test_parse_simple_query()
{
    String header, param;
    bool isQuery;

    scpiParse("*IDN?", header, param, isQuery);

    TEST_ASSERT_EQUAL_STRING("*IDN", header.c_str());
    TEST_ASSERT_EQUAL_STRING("", param.c_str());
    TEST_ASSERT_TRUE(isQuery);
}

void test_parse_command_with_param()
{
    String header, param;
    bool isQuery;

    scpiParse("CONF:ADC:GAIN 16", header, param, isQuery);

    TEST_ASSERT_EQUAL_STRING("CONF:ADC:GAIN", header.c_str());
    TEST_ASSERT_EQUAL_STRING("16", param.c_str());
    TEST_ASSERT_FALSE(isQuery);
}

void test_parse_case_insensitive()
{
    String header, param;
    bool isQuery;

    scpiParse("conf:adc:gain 16", header, param, isQuery);

    TEST_ASSERT_EQUAL_STRING("CONF:ADC:GAIN", header.c_str());
    TEST_ASSERT_EQUAL_STRING("16", param.c_str());
    TEST_ASSERT_FALSE(isQuery);
}

void test_parse_multiple_params()
{
    String header, param;
    bool isQuery;

    scpiParse("CONF:SRC ENC:A,ADC,PDTIA", header, param, isQuery);

    TEST_ASSERT_EQUAL_STRING("CONF:SRC", header.c_str());
    TEST_ASSERT_EQUAL_STRING("ENC:A,ADC,PDTIA", param.c_str());
    TEST_ASSERT_FALSE(isQuery);
}

void test_parse_with_whitespace()
{
    String header, param;
    bool isQuery;

    scpiParse("CONF:RATE  100  ", header, param, isQuery);

    TEST_ASSERT_EQUAL_STRING("CONF:RATE", header.c_str());
    TEST_ASSERT_EQUAL_STRING("100", param.c_str());
    TEST_ASSERT_FALSE(isQuery);
}

void test_parse_query_with_param()
{
    String header, param;
    bool isQuery;

    scpiParse("CONF:ADC:GAIN?", header, param, isQuery);

    TEST_ASSERT_EQUAL_STRING("CONF:ADC:GAIN", header.c_str());
    TEST_ASSERT_TRUE(isQuery);
}

void test_parse_meas_encoder_both()
{
    String header, param;
    bool isQuery;

    scpiParse("MEAS:ENC:ANGL? BOTH", header, param, isQuery);

    TEST_ASSERT_EQUAL_STRING("MEAS:ENC:ANGL", header.c_str());
    TEST_ASSERT_EQUAL_STRING("BOTH", param.c_str());
    TEST_ASSERT_TRUE(isQuery);
}

void test_parse_empty_line()
{
    String header, param;
    bool isQuery;

    bool result = scpiParse("", header, param, isQuery);

    TEST_ASSERT_FALSE(result);
}

// ─── Setup/Teardown ───────────────────────────────────────────────────────

void setUp(void)
{
    // before each test
}

void tearDown(void)
{
    // after each test
}

#endif // UNIT_TEST
