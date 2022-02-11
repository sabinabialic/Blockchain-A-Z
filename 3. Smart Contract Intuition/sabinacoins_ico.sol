// SabinaCoin ICO
// In etherwallet-v3.40.0 open index.html to access MyEtherWallet.com to deploy and interact with the smart contract
// To make changes, compile this code, get the ABI and Byte Code, use remix.etherum.org
// Use Ganache to play with different addresses

// Version of the compiler
pragma solidity ^0.4.11;

contract sabinacoin_ico {
    // Introducing the maximum number of SabinaCoins available for sale; 1 million
    uint public maxSabinaCoins = 1000000;

    // Introducing the USD to SAB conversion rate; 1 USD = 1000 SAB
    uint public usdToSab = 1000;

    // Introducing the total number of SAB that have been bought by investors
    uint public totalSabBought = 0;

    // Mapping from the investor's address to its equity in SAB and USD
    // Input: Address of the investor
    // Output: Uint representing equity
    mapping(address => uint) equitySab;
    mapping(address => uint) equityUsd;

    // Checking if an investor can buy SAB
    modifier canBuySab(uint usdInvested) {
        // The amount of USD invested must be less than the maximum amount of SAB available
        require(usdInvested * usdToSab + totalSabBought <= maxSabinaCoins);
        // The functions to which we will link the modifier will only be applied if the condition is true
        _;
    }

    // Getting the investor's equity in SAB
    // Input: Investor's address, which is a constant that is external to the contract
    // Output: Investor's equity in SAB
    function equityInSab(address investor) external constant returns(uint) {
        return equitySab[investor];
    }

    // Getting the investor's equity in USD
    // Input: Investor's address, which is a constant that is external to the contract
    // Output: Investor's equity in USD
    function equityInUsd(address investor) external constant returns(uint) {
        return equityUsd[investor];
    }

    // Buying SAB
    // Input: Investor's address and the amount of USD they invested
    // Call the modifier to ensure the investor can buy SAB
    function buySab(address investor, uint usdInvested) external canBuySab(usdInvested) {
        // Modify the equity in USD, equity in SAB, total SAB bought
        // Convert the USD invested to Sab and modify their equity in SAB mapping
        uint sabBought = usdInvested * usdToSab;
        equitySab[investor] += sabBought;
        // Update the investor's equity in USD mapping
        equityUsd[investor] = equitySab[investor]/1000;
        // Update the total SAB bought by incrementing it with the amount this investor bought
        totalSabBought += sabBought;
    }

    // Selling SAB
    // Input: Investor's address and the amount of SAB they are selling
    function sellSab(address investor, uint sabSelling) external {
        // Update the investor's new equity in SAB
        equitySab[investor] -= sabSelling;
        // Update the investor's equity in USD mapping
        equityUsd[investor] = equitySab[investor]/1000;
        // Update the total SAB bought by decrementing it with the amount this investor sold
        totalSabBought -= sabSelling;
    }
}
