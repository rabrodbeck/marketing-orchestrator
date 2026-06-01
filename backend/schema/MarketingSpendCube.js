cube(`MarketingSpendCube`, {
  sql: `SELECT * FROM marketing_spend`,

  measures: {
    monthlySpend: {
      sql: `monthlyspend`,
      type: `sum`,
      description: `Active monthly advertising channel investment`
    }
  },

  dimensions: {
    propertyId: {
      sql: `propertyid`,
      type: `string`,
      primaryKey: true
    },
    channel: {
      sql: `channel`,
      type: `string`
    }
  }
});