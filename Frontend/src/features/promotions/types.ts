export type Promotion = {
  id: string
  name: string
  appliesTo: string
  discountType: string
  discountValue: number
  from: string
  to: string
  active: boolean
}
