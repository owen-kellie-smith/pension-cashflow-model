using System.Collections.Generic;
using System.Globalization;
using System.IO;
using CsvHelper;
using PensionModel.Models;

namespace PensionModel.IO
{
    public static class CashflowCsvWriter
    {
        public static void Write(List<Cashflow> cashflows, string path)
        {
            if (path == null) return;

            using var writer = new StreamWriter(path);
            using var csv = new CsvHelper.CsvWriter(writer, CultureInfo.InvariantCulture);

            csv.WriteHeader<Cashflow>();
            csv.NextRecord();
            csv.WriteRecords(cashflows);
        }
    }
}
