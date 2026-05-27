using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Azure.Cosmos;
using Microsoft.Extensions.Configuration;

namespace ChangeFeedDemo
{
    public class Product
    {
        public string id { get; set; }
        public string name { get; set; }
    }

    internal class Program
    {
        private static async Task Main(string[] args)
        {
            // 1. Load configuration (connection string + names)
            IConfiguration config = new ConfigurationBuilder()
                .AddJsonFile("appsettings.json", optional: true)
                .AddEnvironmentVariables()
                .Build();

            string connectionString = config["CosmosConnectionString"];
            string databaseId = config["DatabaseId"] ?? "ai-demo";
            string monitoredContainerId = config["MonitoredContainerId"] ?? "products";
            string leaseContainerId = config["LeaseContainerId"] ?? "leases";

            CosmosClient client = new CosmosClient(connectionString);

            Container monitoredContainer = client.GetContainer(databaseId, monitoredContainerId);
            Container leaseContainer = client.GetContainer(databaseId, leaseContainerId);

            // 2. Build the change feed processor
            ChangeFeedProcessor changeFeedProcessor =
                monitoredContainer
                    .GetChangeFeedProcessorBuilder<Product>(
                        processorName: "ai200-demo-processor",
                        onChangesDelegate: HandleChangesAsync)
                    .WithInstanceName("console-host")
                    .WithLeaseContainer(leaseContainer)
                    .Build();

            Console.WriteLine("Starting change feed processor...");
            await changeFeedProcessor.StartAsync();
            Console.WriteLine("Change feed processor started.");
            Console.WriteLine("Now add or update items in the 'products' container to see events.");

            Console.WriteLine("Press ENTER to stop.");
            Console.ReadLine();

            Console.WriteLine("Stopping change feed processor...");
            await changeFeedProcessor.StopAsync();
            Console.WriteLine("Stopped. Press ENTER to exit.");
            Console.ReadLine();
        }

        // 3. This method is called whenever there are new changes
        private static async Task HandleChangesAsync(
            IReadOnlyCollection<Product> changes,
            CancellationToken cancellationToken)
        {
            Console.WriteLine($"Changes received: {changes.Count}");

            foreach (var product in changes)
            {
                Console.WriteLine($"Change detected: id={product.id}, name={product.name}");
            }

            // Simulate some async work if you want
            await Task.CompletedTask;
        }
    }
}
