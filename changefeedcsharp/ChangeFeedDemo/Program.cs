using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Azure.Cosmos;

namespace ChangeFeedDemo
{
    public class Product
    {
        public string id { get; set; }
        public string name { get; set; }
    }

    internal class Program
    {
        // For teaching: set this to your Cosmos connection string,
        // or read it from an environment variable.
        private const string ConnectionString = "YOUR_COSMOS_CONNECTION_STRING";
        private const string DatabaseId = "ai-demo";
        private const string MonitoredContainerId = "products";
        private const string LeaseContainerId = "leases";

        private static async Task Main(string[] args)
        {
            CosmosClient client = new CosmosClient(ConnectionString);

            Microsoft.Azure.Cosmos.Container monitoredContainer =
                client.GetContainer(DatabaseId, MonitoredContainerId);

            Microsoft.Azure.Cosmos.Container leaseContainer =
                client.GetContainer(DatabaseId, LeaseContainerId);

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

        private static Task HandleChangesAsync(
            IReadOnlyCollection<Product> changes,
            CancellationToken cancellationToken)
        {
            Console.WriteLine($"Changes received: {changes.Count}");

            foreach (var product in changes)
            {
                Console.WriteLine($"Change detected: id={product.id}, name={product.name}");
            }

            return Task.CompletedTask;
        }
    }
}