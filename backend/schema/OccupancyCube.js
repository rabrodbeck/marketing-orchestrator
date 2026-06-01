cube(`OccupancyCube`, {
  sql: `SELECT p.*, t.targetrate FROM properties p LEFT JOIN occupancy_targets t ON p.id = t.propertyid`,

  measures: {
    totalUnits: {
      sql: `totalunits`,
      type: `sum`,
      description: `Total physical units`
    },
    occupiedUnits: {
      sql: `occupiedunits`,
      type: `sum`,
      description: `Number of leased units`
    },
    occupancyRate: {
      sql: `CAST(occupiedunits AS float) / totalunits`,
      type: `avg`,
      description: `Calculated occupancy ratio`
    },
    targetRate: {
      sql: `targetrate`,
      type: `avg`,
      description: `Stated target occupancy rate`
    }
  },

  dimensions: {
    id: {
      sql: `id`,
      type: `string`,
      primaryKey: true
    },
    name: {
      sql: `name`,
      type: `string`
    }
  }
});