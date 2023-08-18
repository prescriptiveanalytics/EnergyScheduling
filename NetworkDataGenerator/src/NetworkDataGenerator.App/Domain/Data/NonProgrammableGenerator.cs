using System;
using System.Collections.Generic;
using System.Text;

namespace NetworkDataGenerator.App.Domain.Data
{
    public enum NonProgrammableGeneratorType
    {
        Photovoltaic = 1,
        PowerWind = 2
    }

    public class NonProgrammableGenerator : INetComponent
    {
        public Bus Bus { get; }
        public int Id { get; }
        public double Capacity { get; set; }
        public NonProgrammableGeneratorType Type { get; set; }

        public NonProgrammableGenerator(Bus bus, int id)
        {
            Bus = bus;
            Id = id;
        }
    }
}
