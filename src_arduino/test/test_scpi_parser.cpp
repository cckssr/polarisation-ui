#include <unity.h>
#include <string>
#include <cctype>
#include <cstring>

// ─── Minimal Arduino String mock for native testing ────────────────────────
// Provides just the subset of Arduino's String API that scpi_parse.inc uses,
// so the parser's actual source can be included and tested here unmodified
// instead of a hand-copied duplicate that could silently drift from it.
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

// Define String as StringMock for the parser under test.
#define String StringMock

// The real parser — same source scpi.cpp compiles into the firmware.
#include "../src/scpi_parse.inc"

// ─── Tests ────────────────────────────────────────────────────────────────

void setUp(void) {}
void tearDown(void) {}

void test_parse_simple_query(void)
{
    String header, param;
    bool isQuery;

    scpiParse("*IDN?", header, param, isQuery);

    TEST_ASSERT_EQUAL_STRING("*IDN", header.c_str());
    TEST_ASSERT_EQUAL_STRING("", param.c_str());
    TEST_ASSERT_TRUE(isQuery);
}

void test_parse_command_with_param(void)
{
    String header, param;
    bool isQuery;

    scpiParse("CONF:ADC:GAIN 16", header, param, isQuery);

    TEST_ASSERT_EQUAL_STRING("CONF:ADC:GAIN", header.c_str());
    TEST_ASSERT_EQUAL_STRING("16", param.c_str());
    TEST_ASSERT_FALSE(isQuery);
}

void test_parse_case_insensitive(void)
{
    String header, param;
    bool isQuery;

    scpiParse("conf:adc:gain 16", header, param, isQuery);

    TEST_ASSERT_EQUAL_STRING("CONF:ADC:GAIN", header.c_str());
    TEST_ASSERT_EQUAL_STRING("16", param.c_str());
    TEST_ASSERT_FALSE(isQuery);
}

void test_parse_multiple_params(void)
{
    String header, param;
    bool isQuery;

    scpiParse("CONF:SRC ENC:A,ADC,PDTIA", header, param, isQuery);

    TEST_ASSERT_EQUAL_STRING("CONF:SRC", header.c_str());
    TEST_ASSERT_EQUAL_STRING("ENC:A,ADC,PDTIA", param.c_str());
    TEST_ASSERT_FALSE(isQuery);
}

void test_parse_with_whitespace(void)
{
    String header, param;
    bool isQuery;

    scpiParse("CONF:RATE  100  ", header, param, isQuery);

    TEST_ASSERT_EQUAL_STRING("CONF:RATE", header.c_str());
    TEST_ASSERT_EQUAL_STRING("100", param.c_str());
    TEST_ASSERT_FALSE(isQuery);
}

void test_parse_query_with_param(void)
{
    String header, param;
    bool isQuery;

    scpiParse("CONF:ADC:GAIN?", header, param, isQuery);

    TEST_ASSERT_EQUAL_STRING("CONF:ADC:GAIN", header.c_str());
    TEST_ASSERT_TRUE(isQuery);
}

void test_parse_meas_encoder_both(void)
{
    String header, param;
    bool isQuery;

    scpiParse("MEAS:ENC:ANGL? BOTH", header, param, isQuery);

    TEST_ASSERT_EQUAL_STRING("MEAS:ENC:ANGL", header.c_str());
    TEST_ASSERT_EQUAL_STRING("BOTH", param.c_str());
    TEST_ASSERT_TRUE(isQuery);
}

void test_parse_empty_line(void)
{
    String header, param;
    bool isQuery;

    bool result = scpiParse("", header, param, isQuery);

    TEST_ASSERT_FALSE(result);
}

void test_parse_sens_query(void)
{
    String header, param;
    bool isQuery;

    scpiParse("SENS:ADC:VREF?", header, param, isQuery);

    TEST_ASSERT_EQUAL_STRING("SENS:ADC:VREF", header.c_str());
    TEST_ASSERT_TRUE(isQuery);
}

// ─── Main Test Runner ─────────────────────────────────────────────────────

int main(void)
{
    UNITY_BEGIN();

    RUN_TEST(test_parse_simple_query);
    RUN_TEST(test_parse_command_with_param);
    RUN_TEST(test_parse_case_insensitive);
    RUN_TEST(test_parse_multiple_params);
    RUN_TEST(test_parse_with_whitespace);
    RUN_TEST(test_parse_query_with_param);
    RUN_TEST(test_parse_meas_encoder_both);
    RUN_TEST(test_parse_empty_line);
    RUN_TEST(test_parse_sens_query);

    return UNITY_END();
}
