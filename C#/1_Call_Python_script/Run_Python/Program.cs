using System.Diagnostics;

var process = new Process();
process.StartInfo.FileName = "python3";
process.StartInfo.Arguments = "run_model.py -mp assets/csv/MPF.csv -a assets/xls -n 30 -r 0.03 -agg sum_year -o output.csv";
// Set the working directory to where your Python script lives
process.StartInfo.WorkingDirectory = @"../../../";
process.StartInfo.RedirectStandardOutput = true;
process.StartInfo.UseShellExecute = false;

process.Start();

string output = process.StandardOutput.ReadToEnd();
process.WaitForExit();

Console.WriteLine(output);
