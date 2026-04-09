using System.Collections.Generic;
using System.Data;
using System.IO;
using System.Text;
using ExcelDataReader;
using PensionModel.Models;

namespace PensionModel.IO
{
    public static class MortalityReader
    {
        public static List<MortalityRow> Read(string file, string folder)
        {
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);

            var path = Path.Combine(folder ?? "", file);

            var result = new List<MortalityRow>();

            using var stream = File.Open(path, FileMode.Open, FileAccess.Read);
            using var reader = ExcelReaderFactory.CreateReader(stream);

            var dataset = reader.AsDataSet();
            DataTable table = dataset.Tables[0];

            for (int i = 1; i < table.Rows.Count; i++) // skip header
            {
                var row = table.Rows[i];

                if (row[0] == null || row[1] == null)
                    continue;

                if (!int.TryParse(row[0].ToString(), out int age))
                    continue;

                if (!double.TryParse(row[1].ToString(), out double qx))
                    continue;

                result.Add(new MortalityRow
                {
                    Age = age,
                    Qx = qx
                });
            }

            return result;
        }
    }
}
