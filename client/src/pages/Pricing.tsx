import { Box, Container } from '@chakra-ui/react'
import Navbar from '../components/Navbar'
import PricingPlans from '../components/PricingPlans'





export default function PricingPage() {
  return (
    <Box bg="bg" minH="100vh">
      <Navbar />
      <Container maxW="6xl" py={10}>
        <PricingPlans />
      </Container>
    </Box>
  )
}
