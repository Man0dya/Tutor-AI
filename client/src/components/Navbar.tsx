import { Box, Button, Flex, HStack, Heading, Spacer, Avatar, Text, Menu, MenuButton, MenuList, MenuItem, MenuDivider, useDisclosure } from '@chakra-ui/react'
import { Link as RouterLink, useNavigate } from 'react-router-dom'
import { IoSettings, IoLogOut, IoChevronDown } from 'react-icons/io5'
import { useAuth } from '../context/AuthContext'
import UserProfileModal from './UserProfileModal'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const { isOpen: isProfileModalOpen, onOpen: onProfileModalOpen, onClose: onProfileModalClose } = useDisclosure()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <Box 
      as="header" 
      bg="white" 
      borderBottomWidth="1px" 
      borderColor="gray.200"
      py={4} 
      px={6}
      boxShadow="0 1px 3px rgba(0, 0, 0, 0.05)"
    >
      <Flex align="center" gap={4}>
        <Heading 
          size="lg" 
          bgGradient="linear(to-r, purple.500, blue.500)"
          bgClip="text"
          fontWeight="bold"
        >
          <RouterLink to={user ? '/dashboard' : '/'}>Tutor AI</RouterLink>
        </Heading>
        <Spacer />
        {user ? (
          <>
            <Menu>
              <MenuButton
                as={Button}
                variant="ghost"
                size="sm"
                rightIcon={<IoChevronDown />}
                borderRadius="lg"
                _hover={{ bg: 'gray.100' }}
                _active={{ bg: 'gray.200' }}
              >
                <Flex align="center" gap={3}>
                  <Avatar size="sm" name={user.name || user.email} bg="purple.500" />
                  <Text fontSize="sm" fontWeight="500" color="gray.700">
                    {user.name || user.email}
                  </Text>
                </Flex>
              </MenuButton>
              <MenuList
                borderRadius="lg"
                border="1px solid"
                borderColor="gray.200"
                boxShadow="lg"
                py={2}
              >
                <MenuItem
                  icon={<IoSettings />}
                  onClick={onProfileModalOpen}
                  borderRadius="md"
                  mx={2}
                  _hover={{ bg: 'purple.50' }}
                >
                  Settings
                </MenuItem>
                <MenuDivider />
                <MenuItem
                  icon={<IoLogOut />}
                  onClick={handleLogout}
                  borderRadius="md"
                  mx={2}
                  _hover={{ bg: 'red.50' }}
                  color="red.600"
                >
                  Logout
                </MenuItem>
              </MenuList>
            </Menu>
            <UserProfileModal isOpen={isProfileModalOpen} onClose={onProfileModalClose} />
          </>
        ) : (
          <HStack spacing={3}>
            <Button 
              as={RouterLink} 
              to="/login" 
              size="sm" 
              variant="outline"
              borderRadius="8px"
              className="btn-professional"
            >
              Login
            </Button>
            <Button 
              as={RouterLink} 
              to="/signup" 
              size="sm" 
              colorScheme="purple"
              borderRadius="8px"
              className="btn-professional"
            >
              Sign Up
            </Button>
          </HStack>
        )}
      </Flex>
    </Box>
  )
}
