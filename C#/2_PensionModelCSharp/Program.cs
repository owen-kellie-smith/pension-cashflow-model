using System;
using System.Collections.Generic;
using PensionModel.Models;
using PensionModel.IO;
using PensionModel.Engine;
using PensionModel.Aggregation;

namespace PensionModel
{
    class Program
    {
        static void PrintHelp()
        {
            Console.WriteLine(@"
Pension Cashflow Model

Usage:
  dotnet run -- [options]

Options:
  --mort <file>        Mortality table file (xls/xlsx)
  --assets <folder>    Folder containing mortality files
  --age <number>       Age at valuation date
  --benefit <number>   Annual pension benefit
  --years <number>     Projection years
  --rate <number>      Discount rate
  --mp <file>          Model points CSV
  --agg <type>         Aggregation type (sum, sum_year)
  --output <file>      Output CSV file
  --debug              Enable debug logging
  --help, -h           Show this help

Examples:

Single life:
  dotnet run -- --mort pma92.xls --assets ../../assets/xls --age 65 --benefit 10000 --years 10

Portfolio run:
  dotnet run -- --mp mp.csv --assets ../../assets/xls --years 10 --output result.csv
");
        }

        static void Main(string[] args)
        {
            if (args.Length == 0)
            {
                PrintHelp();
                return;
            }

            string mpFile = null;
            string assetsFolder = null;
            string mortFile = null;
            string output = null;

            double age = 65;
            double benefit = 10000;
            double rate = 0.03;
            int years = 10;

            string agg = "sum";
            bool debug = false;

            for (int i = 0; i < args.Length; i++)
            {
                string arg = args[i];

                switch (arg)
                {
                    case "--help":
                    case "-h":
                        PrintHelp();
                        return;

                    case "--mp":
                        mpFile = args[++i];
                        break;

                    case "--assets":
                        assetsFolder = args[++i];
                        break;

                    case "--mort":
                        mortFile = args[++i];
                        break;

                    case "--age":
                        age = double.Parse(args[++i]);
                        break;

                    case "--benefit":
                        benefit = double.Parse(args[++i]);
                        break;

                    case "--years":
                        years = int.Parse(args[++i]);
                        break;

                    case "--rate":
                        rate = double.Parse(args[++i]);
                        break;

                    case "--agg":
                        agg = args[++i];
                        break;

                    case "--output":
                        output = args[++i];
                        break;

                    case "--debug":
                        debug = true;
                        break;

                    default:
                        Console.WriteLine($"Unknown argument: {arg}");
                        Console.WriteLine("Use --help to see available options.");
                        return;
                }
            }

            List<ModelPoint> modelPoints =
                ModelPointReader.Load(mpFile, mortFile, age, benefit);

            var mortalityCache = new Dictionary<string, List<MortalityRow>>();
            var allCashflows = new List<Cashflow>();

            foreach (var mp in modelPoints)
            {
                if (!mortalityCache.ContainsKey(mp.Mortality))
                {
                    mortalityCache[mp.Mortality] =
                        MortalityReader.Read(mp.Mortality, assetsFolder);
                }

                var mortality = mortalityCache[mp.Mortality];

                allCashflows.AddRange(
                    PensionCalculator.Calculate(mortality, mp, years, rate)
                );
            }

            var aggregated =
                CashflowAggregator.Aggregate(allCashflows, agg);

            CashflowCsvWriter.Write(aggregated, output);

            if (debug)
                Console.WriteLine($"Processed {modelPoints.Count} model points");
        }
    }
}
