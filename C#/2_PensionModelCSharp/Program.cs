using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using ExcelDataReader;
using CsvHelper;
using CsvHelper.Configuration;
using System.Globalization;

class Program
{
    // ------------------------------
    // Data Models
    // ------------------------------
    public class MortalityRow
    {
        public int Age { get; set; }
        public double Qx { get; set; }
    }

    public class ModelPoint
    {
        public string Mortality { get; set; }
        public double AgeAtVDate { get; set; }
        public double BenefitPA { get; set; }
    }

    public class Cashflow
    {
        public int Year { get; set; }
        public double BenefitPP { get; set; }
        public double SurvivalProb { get; set; }
        public double CashflowValue { get; set; }
        public double DiscountFactor { get; set; }
        public double PresentValue { get; set; }
        public int Record { get; set; } // For aggregation
    }

    // ------------------------------
    // MAIN
    // ------------------------------
    static void Main(string[] args)
    {
        // Defaults
        string mpFile = null;
        string assetsFolder = null;
        int nYears = 10;
        double r = 0.03;
        string aggType = "sum";
        string outputFile = null;

        // Simple CLI parser
        for (int i = 0; i < args.Length; i++)
        {
            switch (args[i])
            {
                case "-mp":
                    mpFile = args[++i];
                    break;
                case "-a":
                    assetsFolder = args[++i];
                    break;
                case "-n":
                    nYears = int.Parse(args[++i]);
                    break;
                case "-r":
                    r = double.Parse(args[++i]);
                    break;
                case "-agg":
                    aggType = args[++i];
                    break;
                case "-o":
                    outputFile = args[++i];
                    break;
                default:
                    Console.WriteLine($"Unknown argument: {args[i]}");
                    break;
            }
        }

        if (mpFile == null || assetsFolder == null)
        {
            Console.WriteLine("Must specify -mp (model points CSV) and -a (assets folder).");
            return;
        }

        var mpList = ReadModelPoints(mpFile);
        var mortalityCache = new Dictionary<string, List<MortalityRow>>();
        var allCashflows = new List<Cashflow>();

        int recordNum = 1;
        foreach (var mp in mpList)
        {
            string mortPath = Path.Combine(assetsFolder, mp.Mortality);
            if (!mortalityCache.ContainsKey(mortPath))
                mortalityCache[mortPath] = ReadMortalityExcel(mortPath);

            var cashflows = CalculatePensionCashflows(
                mortalityCache[mortPath], mp.AgeAtVDate, mp.BenefitPA, nYears, r);

            // Add record number for aggregation
            cashflows.ForEach(cf => cf.Record = recordNum++);
            allCashflows.AddRange(cashflows);
        }

        var aggregated = AggregateCashflows(allCashflows, aggType);

        // Write to CSV
        if (outputFile != null)
            WriteAggregatedCsv(outputFile, aggregated);

        Console.WriteLine($"Aggregated results written to {outputFile ?? "console"}");
    }

    // ------------------------------
    // Read model points CSV
    // ------------------------------
static List<ModelPoint> ReadModelPoints(string path)
{
    using var reader = new StreamReader(path);
    using var csv = new CsvReader(reader, new CsvConfiguration(CultureInfo.InvariantCulture)
    {
        HasHeaderRecord = true
    });

    var records = new List<ModelPoint>();

    // Read header first
    csv.Read();
    csv.ReadHeader();

    while (csv.Read())
    {
        records.Add(new ModelPoint
        {
            Mortality = csv.GetField("mortality"),
            AgeAtVDate = csv.GetField<double>("age_at_vdate"),
            BenefitPA = csv.GetField<double>("benefit_pa")
        });
    }
    return records;
}

    // ------------------------------
    // Read Excel mortality table
    // ------------------------------
    static List<MortalityRow> ReadMortalityExcel(string path)
    {
        System.Text.Encoding.RegisterProvider(System.Text.CodePagesEncodingProvider.Instance);
        var mortality = new List<MortalityRow>();

        using (var stream = File.Open(path, FileMode.Open, FileAccess.Read))
        {
            using var reader = ExcelReaderFactory.CreateReader(stream);
            var ds = reader.AsDataSet();
            var table = ds.Tables[0];

            for (int i = 2; i < table.Rows.Count; i++)
            {
                if (table.Rows[i][0] == null || table.Rows[i][1] == null) continue;
                if (int.TryParse(table.Rows[i][0].ToString(), out int age) &&
                    double.TryParse(table.Rows[i][1].ToString(), out double qx))
                    mortality.Add(new MortalityRow { Age = age, Qx = qx });
            }
        }
        return mortality;
    }

    // ------------------------------
    // Calculate cashflows for one model point
    // ------------------------------
    static List<Cashflow> CalculatePensionCashflows(List<MortalityRow> mortality, double startingAge, double benefitPA, int nYears, double discountRate)
    {
        var survival = SurvivalFunction(startingAge, nYears, mortality);
        var cashflows = new List<Cashflow>();

        for (int t = 0; t < nYears; t++)
        {
            double cashflow = benefitPA * survival[t];
            double discount = Math.Pow(1 + discountRate, -(t + 1));
            cashflows.Add(new Cashflow
            {
                Year = t + 1,
                BenefitPP = benefitPA,
                SurvivalProb = survival[t],
                CashflowValue = cashflow,
                DiscountFactor = discount,
                PresentValue = cashflow * discount
            });
        }
        return cashflows;
    }

    static double[] SurvivalFunction(double ageStart, int nYears, List<MortalityRow> mortality)
    {
        var survival = new double[nYears];
        double prob = 1.0;

        for (int t = 0; t < nYears; t++)
        {
            double age = ageStart + t;
            var lower = mortality.LastOrDefault(m => m.Age <= age);
            var upper = mortality.FirstOrDefault(m => m.Age >= age);

            double qx = 1.0;
            if (lower != null && upper != null)
            {
                if (upper.Age == lower.Age)
                    qx = lower.Qx;
                else
                    qx = lower.Qx + (upper.Qx - lower.Qx) * (age - lower.Age) / (upper.Age - lower.Age);
            }
            else if (lower != null) qx = lower.Qx;
            else if (upper != null) qx = upper.Qx;

            prob *= 1 - qx;
            survival[t] = prob;
        }

        return survival;
    }

    // ------------------------------
    // Aggregation
    // ------------------------------
    static List<Cashflow> AggregateCashflows(List<Cashflow> cashflows, string aggType)
    {
        switch (aggType.ToLower())
        {
            case "sum":
                double totalBenefit = cashflows.Sum(cf => cf.BenefitPP);
                double totalCash = cashflows.Sum(cf => cf.CashflowValue);
                double totalPV = cashflows.Sum(cf => cf.PresentValue);
                return new List<Cashflow>
                {
                    new Cashflow { Year = 0, BenefitPP = totalBenefit, CashflowValue = totalCash, PresentValue = totalPV }
                };

            case "sum_year":
                var sumYear = cashflows
                    .GroupBy(cf => cf.Year)
                    .Select(g => new Cashflow
                    {
                        Year = g.Key,
                        BenefitPP = g.Sum(cf => cf.BenefitPP),
                        CashflowValue = g.Sum(cf => cf.CashflowValue),
                        PresentValue = g.Sum(cf => cf.PresentValue)
                    }).ToList();
                return sumYear;

            case "sum_record":
                var sumRecord = cashflows
                    .GroupBy(cf => cf.Record)
                    .Select(g => new Cashflow
                    {
                        Year = g.First().Year, // arbitrary
                        BenefitPP = g.Sum(cf => cf.BenefitPP),
                        CashflowValue = g.Sum(cf => cf.CashflowValue),
                        PresentValue = g.Sum(cf => cf.PresentValue)
                    }).ToList();
                return sumRecord;

            case "year_record":
                return cashflows.OrderBy(cf => cf.Year).ThenBy(cf => cf.Record).ToList();

            default:
                throw new Exception("Invalid aggregation type. Use sum, sum_year, sum_record, year_record.");
        }
    }

    // ------------------------------
    // Write aggregated CSV
    // ------------------------------
    static void WriteAggregatedCsv(string path, List<Cashflow> cashflows)
    {
        using var writer = new StreamWriter(path);
        writer.WriteLine("Year,BenefitPP,Cashflow,PresentValue");
        foreach (var cf in cashflows)
        {
            writer.WriteLine($"{cf.Year},{cf.BenefitPP},{cf.CashflowValue},{cf.PresentValue}");
        }
    }
}
