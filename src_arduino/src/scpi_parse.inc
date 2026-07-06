// SCPI line parser — split into header/param/isQuery.
//
// #included (not compiled as its own translation unit) so both scpi.cpp
// (real firmware, String = Arduino's String) and test/test_scpi_parser.cpp
// (native unit test, String = a lightweight StringMock) each compile this
// exact same source against their own String implementation. This is the
// single source of truth for the parser — do not copy it elsewhere.

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
