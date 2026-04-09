using System.Collections.Generic;
using System.Linq;
using PensionModel.Models;

namespace PensionModel.Aggregation
{
    public static class CashflowAggregator
    {
        public static List<Cashflow> Aggregate(
            List<Cashflow> cashflows,
            string type)
        {
            if (type == "sum_year")
            {
                return cashflows
                    .GroupBy(c => c.Year)
                    .Select(g => new Cashflow
                    {
                        Year = g.Key,
                        CashflowValue = g.Sum(c => c.CashflowValue),
                        PresentValue = g.Sum(c => c.PresentValue)
                    })
                    .ToList();
            }

            return new List<Cashflow>
            {
                new Cashflow
                {
                    Year = 0,
                    CashflowValue = cashflows.Sum(c => c.CashflowValue),
                    PresentValue = cashflows.Sum(c => c.PresentValue)
                }
            };
        }
    }
}
