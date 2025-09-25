import React, { useState } from 'react';
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  useToast,
  Text,
  Divider,
  InputGroup,
  InputRightElement,
  IconButton
} from '@chakra-ui/react';
import { IoEye, IoEyeOff } from 'react-icons/io5';
import { useAuth } from '../context/AuthContext';
import { updateProfile, getErrorMessage, createBillingPortal, cancelSubscription, resumeSubscription } from '../api/client';

interface UserProfileModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const UserProfileModal: React.FC<UserProfileModalProps> = ({ isOpen, onClose }) => {
  const { user, refreshUser, plan, subscription, refreshBilling, upgrade } = useAuth();
  const toast = useToast();
  
  // Form state
  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      // Validate password confirmation if changing password
      if (formData.newPassword && formData.newPassword !== formData.confirmPassword) {
        toast({
          title: 'Password Mismatch',
          description: 'New password and confirmation do not match.',
          status: 'error',
          duration: 3000,
          isClosable: true,
        });
        return;
      }

      // Prepare API request data
      const updateData: any = {
        name: formData.name,
        email: formData.email,
      };

      // Add password fields if changing password
      if (formData.newPassword) {
        if (!formData.currentPassword) {
          toast({
            title: 'Current Password Required',
            description: 'Please enter your current password to change it.',
            status: 'error',
            duration: 3000,
            isClosable: true,
          });
          return;
        }
        updateData.current_password = formData.currentPassword;
        updateData.new_password = formData.newPassword;
      }

      // Call API to update profile
      await updateProfile(updateData);

      // Refresh user data in context
      await refreshUser();

      toast({
        title: 'Profile Updated',
        description: 'Your profile has been updated successfully.',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });

      // Reset password fields
      setFormData(prev => ({
        ...prev,
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      }));

      onClose();
    } catch (error) {
      toast({
        title: 'Update Failed',
        description: getErrorMessage(error),
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    // Reset form data when closing
    setFormData({
      name: user?.name || '',
      email: user?.email || '',
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    });
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} size="2xl">
      <ModalOverlay bg="blackAlpha.300" backdropFilter="blur(10px)" />
      <ModalContent mx={4} borderRadius="xl" boxShadow="xl">
        <ModalHeader>
          <Text fontSize="xl" fontWeight="bold" color="gray.800">
            Profile Settings
          </Text>
        </ModalHeader>
        <ModalCloseButton />
        
        <form onSubmit={handleSubmit}>
          <ModalBody pb={6}>
            <VStack spacing={6} align="stretch">
              {/* Personal Information Section */}
              <VStack spacing={4} align="stretch">
                <Text fontSize="md" fontWeight="semibold" color="gray.700">
                  Personal Information
                </Text>
                
                <FormControl isRequired>
                  <FormLabel color="gray.600">Full Name</FormLabel>
                  <Input
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    placeholder="Enter your full name"
                    borderRadius="lg"
                    focusBorderColor="purple.400"
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel color="gray.600">Email Address</FormLabel>
                  <Input
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    placeholder="Enter your email address"
                    borderRadius="lg"
                    focusBorderColor="purple.400"
                  />
                </FormControl>
              </VStack>

              <Divider />

              {/* Password Change Section */}
              <VStack spacing={4} align="stretch">
                <Text fontSize="md" fontWeight="semibold" color="gray.700">
                  Change Password (Optional)
                </Text>
                <Text fontSize="sm" color="gray.500">
                  Leave blank to keep your current password
                </Text>

                <FormControl>
                  <FormLabel color="gray.600">Current Password</FormLabel>
                  <InputGroup>
                    <Input
                      name="currentPassword"
                      type={showCurrentPassword ? 'text' : 'password'}
                      value={formData.currentPassword}
                      onChange={handleInputChange}
                      placeholder="Enter current password"
                      borderRadius="lg"
                      focusBorderColor="purple.400"
                    />
                    <InputRightElement>
                      <IconButton
                        aria-label={showCurrentPassword ? 'Hide password' : 'Show password'}
                        icon={showCurrentPassword ? <IoEyeOff /> : <IoEye />}
                        onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                        variant="ghost"
                        size="sm"
                      />
                    </InputRightElement>
                  </InputGroup>
                </FormControl>

                <FormControl>
                  <FormLabel color="gray.600">New Password</FormLabel>
                  <InputGroup>
                    <Input
                      name="newPassword"
                      type={showNewPassword ? 'text' : 'password'}
                      value={formData.newPassword}
                      onChange={handleInputChange}
                      placeholder="Enter new password"
                      borderRadius="lg"
                      focusBorderColor="purple.400"
                    />
                    <InputRightElement>
                      <IconButton
                        aria-label={showNewPassword ? 'Hide password' : 'Show password'}
                        icon={showNewPassword ? <IoEyeOff /> : <IoEye />}
                        onClick={() => setShowNewPassword(!showNewPassword)}
                        variant="ghost"
                        size="sm"
                      />
                    </InputRightElement>
                  </InputGroup>
                </FormControl>

                <FormControl>
                  <FormLabel color="gray.600">Confirm New Password</FormLabel>
                  <InputGroup>
                    <Input
                      name="confirmPassword"
                      type={showConfirmPassword ? 'text' : 'password'}
                      value={formData.confirmPassword}
                      onChange={handleInputChange}
                      placeholder="Confirm new password"
                      borderRadius="lg"
                      focusBorderColor="purple.400"
                    />
                    <InputRightElement>
                      <IconButton
                        aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
                        icon={showConfirmPassword ? <IoEyeOff /> : <IoEye />}
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        variant="ghost"
                        size="sm"
                      />
                    </InputRightElement>
                  </InputGroup>
                </FormControl>
              </VStack>

              <Divider />

              {/* Billing Section */}
              <VStack spacing={4} align="stretch">
                <Text fontSize="md" fontWeight="semibold" color="gray.700">
                  Billing
                </Text>
                <Text fontSize="sm" color="gray.600">
                  Your current plan is <b>{(plan || 'free').toUpperCase()}</b>.
                </Text>
                {plan !== 'free' && (
                  <VStack spacing={2} align="stretch">
                    <Text fontSize="sm" color="gray.600">
                      Status: {subscription?.status ? subscription.status.replace(/_/g, ' ') : '—'}
                    </Text>
                    <Text fontSize="sm" color="gray.600">
                      Renews on: {subscription?.current_period_end ? new Date(subscription.current_period_end * 1000).toLocaleDateString() : '—'}
                    </Text>
                    <Text fontSize="sm" color="gray.600">
                      Next invoice: {subscription?.next_invoice_amount_due != null ? `${(subscription.next_invoice_amount_due/100).toFixed(2)} ${(subscription.next_invoice_currency || 'usd').toUpperCase()}` : '—'}
                    </Text>
                    {subscription?.cancel_at_period_end && (
                      <Text fontSize="sm" color="orange.500" fontWeight="semibold">
                        Cancellation scheduled at period end
                      </Text>
                    )}
                    <VStack align="start" spacing={2} pt={2}>
                      {!subscription?.cancel_at_period_end ? (
                        <Button size="sm" variant="outline" colorScheme="red" onClick={async () => {
                          try {
                            await cancelSubscription(true)
                            await refreshBilling()
                            toast({ title: 'Will cancel at period end', status: 'info', duration: 3000, isClosable: true })
                          } catch (e) {
                            toast({ title: 'Failed to schedule cancel', description: getErrorMessage(e), status: 'error', duration: 4000, isClosable: true })
                          }
                        }}>
                          Cancel at period end
                        </Button>
                      ) : (
                        <Button size="sm" variant="outline" onClick={async () => {
                          try {
                            await resumeSubscription()
                            await refreshBilling()
                            toast({ title: 'Subscription resumed', status: 'success', duration: 3000, isClosable: true })
                          } catch (e) {
                            toast({ title: 'Failed to resume', description: getErrorMessage(e), status: 'error', duration: 4000, isClosable: true })
                          }
                        }}>
                          Resume subscription
                        </Button>
                      )}
                      <Button size="sm" onClick={async () => {
                        try {
                          const p = await createBillingPortal()
                          if (p.url) window.location.assign(p.url)
                        } catch (e) {
                          toast({ title: 'Failed to open billing portal', description: getErrorMessage(e), status: 'error', duration: 4000, isClosable: true })
                        }
                      }}>
                        Manage Billing
                      </Button>
                    </VStack>
                  </VStack>
                )}
                {plan === 'free' && (
                  <VStack align="start" spacing={2}>
                    <Text fontSize="sm" color="gray.600">Upgrade to unlock all features and higher limits.</Text>
                    <Button size="sm" colorScheme="purple" onClick={() => {
                      try { upgrade() } catch {}
                    }}>
                      Upgrade
                    </Button>
                  </VStack>
                )}
              </VStack>
            </VStack>
            
          </ModalBody>

          <ModalFooter>
            <Button 
              variant="outline" 
              mr={3} 
              onClick={handleClose}
              borderRadius="lg"
            >
              Cancel
            </Button>
            <Button 
              type="submit"
              colorScheme="purple" 
              isLoading={isLoading}
              loadingText="Updating..."
              borderRadius="lg"
            >
              Save Changes
            </Button>
          </ModalFooter>
        </form>
      </ModalContent>
    </Modal>
  );
};

export default UserProfileModal;