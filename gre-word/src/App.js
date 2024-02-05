
import { Box, Button, Center, ChakraProvider } from '@chakra-ui/react'

function App() {
  return (
    <ChakraProvider>
      <Box >
        <Center h="100vh" w="100%">
          <Button>hello</Button>
        </Center>
      </Box>
    </ChakraProvider>

  );
}

export default App;
