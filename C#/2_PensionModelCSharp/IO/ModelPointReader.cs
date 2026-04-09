using System.Collections.Generic;
using System.Globalization;
using System.IO;
using CsvHelper;
using PensionModel.Models;

namespace PensionModel.IO
{
    public static class ModelPointReader
    {
        public static List<ModelPoint> Load(
            string mpFile,
            string mortFile,
            double age,
            double benefit)
        {
            if (mpFile == null)
            {
                return new List<ModelPoint>
                {
                    new ModelPoint
                    {
                        Mortality = mortFile,
                        AgeAtVDate = age,
                        BenefitPA = benefit
                    }
                };
            }

            var list = new List<ModelPoint>();

            using var reader = new StreamReader(mpFile);
            using var csv = new CsvReader(reader, CultureInfo.InvariantCulture);

            csv.Read();
            csv.ReadHeader();

            while (csv.Read())
            {
                list.Add(new ModelPoint
                {
                    Mortality = csv.GetField("mortality"),
                    AgeAtVDate = csv.GetField<double>("age_at_vdate"),
                    BenefitPA = csv.GetField<double>("benefit_pa")
                });
            }

            return list;
        }
    }
}
