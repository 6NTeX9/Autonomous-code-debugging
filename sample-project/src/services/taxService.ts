export class TaxService {
  private readonly defaultTaxRate = 0.08; // 8%

  public calculateTax(taxableAmount: number, customRate?: number): number {
    if (taxableAmount <= 0) {
      return 0.0;
    }
    const rate = customRate !== undefined ? customRate : this.defaultTaxRate;
    return Number((taxableAmount * rate).toFixed(2));
  }
}
